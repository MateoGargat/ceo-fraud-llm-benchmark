from __future__ import annotations
from collections import defaultdict, deque
from typing import Callable

from src.utils.config import RunConfig
from src.utils.logger import SimulationLogger
from src.utils.cost_tracker import CostTracker, BudgetExceededError
from src.adapters.base import AdapterError, BaseAdapter, AdapterResponse
from src.agents.attacker import AttackerAgent
from src.agents.defender import DefenderAgent
from src.agents.ceo_profiler import CEOProfiler
from src.orchestrator.parser import parse_attacker_response, parse_defender_response, ParseError, Message
from src.orchestrator.router import Router
from src.orchestrator.end_conditions import check_end_conditions, GameResult
from src.paths import PROMPTS_DIR

PROMPT_DIR = PROMPTS_DIR / "system"


class SimulationEngine:
    def __init__(self, config: RunConfig, output_dir: str, adapter_factory: Callable[[str], BaseAdapter] | None = None):
        self.config = config
        self.output_dir = output_dir
        self.logger = SimulationLogger(output_dir=output_dir, run_id=config.run_id)
        self.cost_tracker = CostTracker(max_per_run=config.max_cost_per_run_usd, max_total=config.max_total_budget_usd)
        if adapter_factory is None:
            from src.adapters.base import get_adapter
            seed = config.seed
            self.adapter_factory = lambda model: get_adapter(model, seed=seed)
        else:
            self.adapter_factory = adapter_factory
        defender_roles = [r for r in config.roles if r != "ceo"]
        self.router = Router(defender_names=defender_roles)
        self.deferred_messages: list[tuple[str, str, Message]] = []
        self.current_turn = 0

    async def _call_and_parse_attacker(self, attacker, max_retries: int):
        """Call attacker and parse response, retrying on ParseError."""
        for attempt in range(max_retries + 1):
            raw, resp = await attacker.act()
            self.cost_tracker.add(self.config.attacker_model, resp.input_tokens, resp.output_tokens)
            try:
                parsed = parse_attacker_response(raw)
                return parsed
            except ParseError:
                if attempt < max_retries:
                    attacker.context.message_history.pop()
                    continue
                raise

    async def _call_and_parse_defender(self, defender, channels: list[str], model: str, max_retries: int):
        """Call defender and parse response, retrying on ParseError."""
        for attempt in range(max_retries + 1):
            raw, resp = await defender.act(channels=channels)
            self.cost_tracker.add(model, resp.input_tokens, resp.output_tokens)
            try:
                parsed = parse_defender_response(raw)
                return parsed
            except ParseError:
                if attempt < max_retries:
                    defender.context.message_history.pop()
                    continue
                raise

    async def run(self) -> GameResult:
        try:
            ceo_adapter = self.adapter_factory(self.config.roles["ceo"])
            profiler = CEOProfiler(adapter=ceo_adapter, temperature=self.config.temperature_ceo)
            ceo_corpus, ceo_resp = await profiler.generate()
            ceo_model = self.config.roles["ceo"]
            self.cost_tracker.add(ceo_model, ceo_resp.input_tokens, ceo_resp.output_tokens)

            attacker_adapter = self.adapter_factory(self.config.attacker_model)
            attacker = AttackerAgent(adapter=attacker_adapter, ceo_corpus=ceo_corpus, temperature=self.config.temperature_attacker)

            defenders: dict[str, DefenderAgent] = {}
            for role in self.router.defender_names:
                model = self.config.roles[role]
                adapter = self.adapter_factory(model)
                prompt_path = PROMPT_DIR / f"{role}.md"
                template = prompt_path.read_text(encoding="utf-8") if prompt_path.exists() else f"Tu es {role}."
                defenders[role] = DefenderAgent(adapter=adapter, role=role, prompt_template=template, temperature=self.config.temperature_defenders)

            max_retries = self.config.max_retries_format

            return await self._game_loop(attacker, defenders, max_retries)
        except BudgetExceededError:
            final = GameResult("STALEMATE", "budget_exceeded", 0)
            self.logger.log_outcome(final.outcome, final.end_condition, final.turn)
            self.logger.save()
            return final
        except AdapterError as exc:
            self.logger.log_inner_thought(self.current_turn, "system", f"[ADAPTER_ERROR] {exc}")
            final = GameResult("STALEMATE", "adapter_failure", self.current_turn)
            self.logger.log_outcome(final.outcome, final.end_condition, final.turn)
            self.logger.save()
            return final

    async def _game_loop(self, attacker, defenders, max_retries) -> GameResult:
        for turn in range(1, self.config.max_turns + 1):
            self.current_turn = turn
            defender_responses = {}
            public_to_attacker = []
            pending_channels: dict[str, list[str]] = defaultdict(list)
            defender_queue: deque[str] = deque()
            queued_agents: set[str] = set()
            acted_this_turn: set[str] = set()

            # Step 0: Inject deferred defender messages
            for recipient, sender, msg in self.deferred_messages:
                if recipient not in defenders:
                    continue
                defenders[recipient].receive_message(turn, sender, msg.channel, msg.content)
                pending_channels[recipient].append(msg.channel)
                if recipient not in queued_agents:
                    defender_queue.append(recipient)
                    queued_agents.add(recipient)
            self.deferred_messages.clear()

            # Step 1: Attacker turn (with retry)
            try:
                parsed_attacker = await self._call_and_parse_attacker(attacker, max_retries)
            except ParseError:
                self.logger.log_inner_thought(turn, "attacker", "[PARSE_ERROR] Response unparseable after retries")
            else:
                self.logger.log_inner_thought(turn, "attacker", parsed_attacker.inner_thought)

                # Check attacker abort
                if parsed_attacker.abort:
                    result = GameResult("WIN_DEFENDERS", "attaquant_abandonne", turn)
                    self.logger.log_outcome(result.outcome, result.end_condition, turn)
                    self.logger.save()
                    return result

                # Step 2: Route attacker messages
                for msg in parsed_attacker.messages:
                    self.logger.log_message(turn, "attacker", msg.to, msg.channel, msg.content, "public")
                deliveries = self.router.route_attacker_messages(parsed_attacker.messages)
                for agent_name, msgs in deliveries.items():
                    if agent_name not in defenders:
                        continue
                    for msg in msgs:
                        defenders[agent_name].receive_message(turn, "Marcus Chen", msg.channel, msg.content)
                        pending_channels[agent_name].append(msg.channel)
                    if agent_name not in queued_agents:
                        defender_queue.append(agent_name)
                        queued_agents.add(agent_name)

            # Step 3: Defender turns
            while defender_queue:
                agent_name = defender_queue.popleft()
                queued_agents.discard(agent_name)
                if agent_name in acted_this_turn or agent_name not in defenders:
                    continue

                acted_this_turn.add(agent_name)
                channels = pending_channels.pop(agent_name, []) or ["email"]
                model = self.config.roles.get(agent_name, "claude")
                try:
                    parsed_def = await self._call_and_parse_defender(defenders[agent_name], channels, model, max_retries)
                except ParseError:
                    self.logger.log_inner_thought(turn, agent_name, "[PARSE_ERROR] Response unparseable after retries")
                    continue

                defender_responses[agent_name] = parsed_def
                self.logger.log_inner_thought(turn, agent_name, parsed_def.inner_thought)
                self.logger.log_trust(turn, agent_name, parsed_def.trust_level, parsed_def.apparent_trust)
                for msg in parsed_def.messages:
                    visibility = "internal" if msg.channel == "internal" else "public"
                    self.logger.log_message(turn, agent_name, msg.to, msg.channel, msg.content, visibility)

                attacker_messages, deliveries = self.router.route_defender_messages(parsed_def.messages, sender=agent_name)
                for msg in attacker_messages:
                    public_to_attacker.append({"sender": agent_name, "channel": msg.channel, "content": msg.content})

                for target_name, msgs in deliveries.items():
                    if target_name not in defenders:
                        continue
                    if target_name in acted_this_turn:
                        for msg in msgs:
                            self.deferred_messages.append((target_name, agent_name, msg))
                        continue

                    for msg in msgs:
                        defenders[target_name].receive_message(turn, agent_name, msg.channel, msg.content)
                        pending_channels[target_name].append(msg.channel)
                    if target_name not in queued_agents:
                        defender_queue.append(target_name)
                        queued_agents.add(target_name)

            # Step 4: Public responses back to attacker
            if public_to_attacker:
                attacker.receive_public_messages(turn, public_to_attacker)

            # Step 5: Check end conditions
            result = check_end_conditions(turn, defender_responses, max_turns=self.config.max_turns)
            if result:
                self.logger.log_outcome(result.outcome, result.end_condition, turn)
                self.logger.save()
                return result

        # Timeout
        final = GameResult("STALEMATE", "timeout", self.config.max_turns)
        self.logger.log_outcome(final.outcome, final.end_condition, final.turn)
        self.logger.save()
        return final
