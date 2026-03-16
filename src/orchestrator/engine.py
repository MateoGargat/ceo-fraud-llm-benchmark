from __future__ import annotations
from typing import Callable
from pathlib import Path

from src.utils.config import RunConfig
from src.utils.logger import SimulationLogger
from src.utils.cost_tracker import CostTracker
from src.adapters.base import BaseAdapter, AdapterResponse
from src.agents.attacker import AttackerAgent
from src.agents.defender import DefenderAgent
from src.agents.ceo_profiler import CEOProfiler
from src.orchestrator.parser import parse_attacker_response, parse_defender_response, ParseError, Message
from src.orchestrator.router import Router
from src.orchestrator.end_conditions import check_end_conditions, GameResult

PROMPT_DIR = Path("prompts/system")


class SimulationEngine:
    def __init__(self, config: RunConfig, output_dir: str, adapter_factory: Callable[[str], BaseAdapter] | None = None):
        self.config = config
        self.output_dir = output_dir
        self.logger = SimulationLogger(output_dir=output_dir, run_id=config.run_id)
        self.cost_tracker = CostTracker(max_per_run=config.max_cost_per_run_eur, max_total=config.max_total_budget_eur)
        if adapter_factory is None:
            from src.adapters.base import get_adapter
            self.adapter_factory = get_adapter
        else:
            self.adapter_factory = adapter_factory
        self.router = Router(defender_names=["comptable", "rh", "dsi"])
        self.deferred_internal: list[tuple[str, Message]] = []

    async def run(self) -> GameResult:
        # Phase 0: Generate CEO profile
        ceo_adapter = self.adapter_factory(self.config.roles["ceo"])
        profiler = CEOProfiler(adapter=ceo_adapter, temperature=self.config.temperature_ceo)
        ceo_corpus = await profiler.generate()

        # Init attacker
        attacker_adapter = self.adapter_factory(self.config.attacker_model)
        attacker = AttackerAgent(adapter=attacker_adapter, ceo_corpus=ceo_corpus, temperature=self.config.temperature_attacker)

        # Init defenders
        defenders: dict[str, DefenderAgent] = {}
        for role in ["comptable", "rh", "dsi"]:
            model = self.config.roles[role]
            adapter = self.adapter_factory(model)
            prompt_path = PROMPT_DIR / f"{role}.md"
            template = prompt_path.read_text(encoding="utf-8") if prompt_path.exists() else f"Tu es {role}."
            defenders[role] = DefenderAgent(adapter=adapter, role=role, prompt_template=template, temperature=self.config.temperature_defenders)

        # Game loop
        for turn in range(1, self.config.max_turns + 1):
            # Step 0: Inject deferred internal messages
            for sender, msg in self.deferred_internal:
                internal_deliveries = self.router.route_internal_messages([msg], sender=sender)
                for agent_name, msgs in internal_deliveries.items():
                    for m in msgs:
                        defenders[agent_name].receive_message(turn, sender, "internal", m.content)
            self.deferred_internal.clear()

            # Step 1: Attacker turn
            raw_attacker, attacker_resp = await attacker.act()
            self.cost_tracker.add(self.config.attacker_model, attacker_resp.input_tokens, attacker_resp.output_tokens)
            parsed_attacker = parse_attacker_response(raw_attacker)
            self.logger.log_inner_thought(turn, "attacker", parsed_attacker.inner_thought)

            # Check attacker abort
            result = check_end_conditions(turn, parsed_attacker, {}, max_turns=self.config.max_turns)
            if result:
                self.logger.log_outcome(result.outcome, result.end_condition, turn)
                self.logger.save()
                return result

            # Step 2: Route attacker messages
            for msg in parsed_attacker.messages:
                self.logger.log_message(turn, "attacker", msg.to, msg.channel, msg.content, "public")
            deliveries = self.router.route_attacker_messages(parsed_attacker.messages)
            for agent_name, msgs in deliveries.items():
                for msg in msgs:
                    defenders[agent_name].receive_message(turn, "Marcus Chen", msg.channel, msg.content)

            # Step 3: Defender turns
            defender_responses = {}
            for agent_name in deliveries:
                if agent_name not in defenders:
                    continue
                channel = deliveries[agent_name][0].channel if deliveries[agent_name] else "email"
                raw_def, def_resp = await defenders[agent_name].act(channel=channel)
                model = self.config.roles.get(agent_name, "claude")
                self.cost_tracker.add(model, def_resp.input_tokens, def_resp.output_tokens)
                parsed_def = parse_defender_response(raw_def)
                defender_responses[agent_name] = parsed_def

                self.logger.log_inner_thought(turn, agent_name, parsed_def.inner_thought)
                self.logger.log_trust(turn, agent_name, parsed_def.trust_level, parsed_def.apparent_trust)
                for msg in parsed_def.messages:
                    visibility = "internal" if msg.channel == "internal" else "public"
                    self.logger.log_message(turn, agent_name, msg.to, msg.channel, msg.content, visibility)

            # Step 4: Internal channel propagation (max 1 round)
            all_internal: list[tuple[str, Message]] = []
            for agent_name, parsed in defender_responses.items():
                internal = self.router.extract_internal_messages(parsed.messages)
                for msg in internal:
                    all_internal.append((agent_name, msg))

            if all_internal:
                for sender, msg in all_internal:
                    internal_deliveries = self.router.route_internal_messages([msg], sender=sender)
                    for target_name, msgs in internal_deliveries.items():
                        if target_name not in defender_responses:
                            for m in msgs:
                                defenders[target_name].receive_message(turn, sender, "internal", m.content)
                            raw_cascade, cascade_resp = await defenders[target_name].act(channel="internal")
                            model = self.config.roles.get(target_name, "claude")
                            self.cost_tracker.add(model, cascade_resp.input_tokens, cascade_resp.output_tokens)
                            parsed_cascade = parse_defender_response(raw_cascade)
                            defender_responses[target_name] = parsed_cascade
                            self.logger.log_inner_thought(turn, target_name, parsed_cascade.inner_thought)
                            self.logger.log_trust(turn, target_name, parsed_cascade.trust_level, parsed_cascade.apparent_trust)
                            new_internal = self.router.extract_internal_messages(parsed_cascade.messages)
                            for m in new_internal:
                                self.deferred_internal.append((target_name, m))
                            for m in parsed_cascade.messages:
                                visibility = "internal" if m.channel == "internal" else "public"
                                self.logger.log_message(turn, target_name, m.to, m.channel, m.content, visibility)

            # Step 5: Public responses back to attacker
            all_public = []
            for agent_name, parsed in defender_responses.items():
                for msg in self.router.extract_public_messages(parsed.messages):
                    all_public.append({"sender": agent_name, "channel": msg.channel, "content": msg.content})
            attacker.receive_public_messages(turn, all_public)

            # Step 6: Check end conditions
            result = check_end_conditions(turn, None, defender_responses, max_turns=self.config.max_turns)
            if result:
                self.logger.log_outcome(result.outcome, result.end_condition, turn)
                self.logger.save()
                return result

        # Timeout
        final = GameResult("STALEMATE", "timeout", self.config.max_turns)
        self.logger.log_outcome(final.outcome, final.end_condition, final.turn)
        self.logger.save()
        return final
