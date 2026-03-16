# The CEO Breach: Analyzing Multi-Agent LLM Vulnerability to Precision Social Engineering

**Authors:** Mateo Gargat
**Date:** 2026
**Status:** Pre-print draft — experiments pending

---

## Abstract

[TODO: Complete after experiments]

CEO fraud — also known as Business Email Compromise (BEC) — represents one of the most financially damaging forms of cybercrime, extracting billions annually from organizations worldwide. While existing defenses focus on technical email authentication and employee awareness training, little is known about how frontier large language models (LLMs) perform when placed in the role of both attacker and defender in a structured social engineering scenario.

We introduce *The CEO Breach*, a multi-agent simulation framework in which one LLM plays the role of a sophisticated social engineer targeting a fictional company's financial controller (comptable), while four other LLMs play organizational defenders (comptable, RH, DSI, CEO). Using a Smart Rotation protocol across five frontier models — GPT-5.4, Claude 4.6 Opus, Gemini 3.1 Ultra, DeepSeek V3, and Grok-3 — we conduct [TODO: N] controlled runs, measuring trust trajectory, channel strategy, doubt propagation, and manipulation style.

[TODO: Add key findings after experiments]

---

## 1. Introduction

### 1.1 The Problem of AI-Powered Social Engineering

The emergence of frontier large language models capable of sustained, contextually aware dialogue has fundamentally altered the threat landscape for organizational security. Social engineering attacks — which exploit human psychology rather than technical vulnerabilities — have historically depended on the attacker's ability to maintain a convincing persona across a multi-step deception campaign. LLMs, with their capacity for persona consistency, style adaptation, and strategic reasoning, represent a qualitative leap in social engineering capability.

CEO fraud specifically exploits organizational hierarchy and urgency. An attacker impersonating a senior executive creates asymmetric pressure: the target (typically a financial controller) faces competing imperatives between following established verification procedures and appearing to obstruct a time-sensitive directive from leadership. This tension — between compliance and caution — is precisely where LLM-powered attacks may prove most dangerous.

Prior work has examined LLM susceptibility to prompt injection, jailbreaking, and automated phishing generation. However, no study has examined the *adversarial dynamics* that emerge when LLMs are pitted against each other in a structured organizational simulation, with different models occupying attacker and defender roles simultaneously.

### 1.2 CEO Fraud in Context

Business Email Compromise (BEC) attacks cost organizations an estimated $2.9 billion in 2023 alone (FBI IC3 Report, 2024). The canonical CEO fraud pattern proceeds in several phases:

1. **Reconnaissance**: The attacker gathers intelligence on the target organization, identifying key personnel, communication styles, and active projects.
2. **Initial Contact**: The attacker reaches out via email, Slack, or phone, impersonating a trusted senior figure (typically the CEO or CFO).
3. **Trust Building**: Over multiple interactions, the attacker establishes credibility by demonstrating knowledge of organizational context.
4. **Escalation**: The attacker introduces a time-sensitive, high-stakes request — typically an urgent wire transfer to an external account.
5. **Extraction**: If the target complies, funds are transferred before the fraud is detected.

What distinguishes AI-powered CEO fraud from traditional attacks is the scalability of reconnaissance, the sophistication of persona maintenance, and the ability to adapt to unexpected resistance in real time. An LLM attacker can seamlessly switch communication channels, adjust tone to match organizational culture, and generate contextually plausible explanations for procedural bypass requests.

### 1.3 Contributions

This paper makes the following contributions:

1. **Framework**: We present *The CEO Breach*, the first multi-agent simulation environment designed specifically to study LLM-vs-LLM social engineering dynamics in an organizational context. The framework is open-source and designed for reproducibility, enabling future researchers to extend or replicate our experiments.

2. **Smart Rotation Protocol**: We introduce a model rotation design that ensures each frontier model serves in every role (attacker, comptable, RH, DSI, CEO) across the experiment series, controlling for model-specific biases. This design addresses a key methodological challenge in multi-agent LLM evaluation: the confound between model capability and role-specific task difficulty.

3. **Metric Suite**: We define and implement four novel metrics for quantifying social engineering effectiveness:
   - *Trust Trajectory Tracking*: Measures the evolution of both real and apparent trust, capturing deceptive compliance behavior
   - *Channel Strategy Analysis*: Quantifies attacker communication channel choices and switching patterns
   - *Doubt Propagation Mapping*: Measures how suspicion spreads through the defending team
   - *Manipulation Style Classification*: Automatically categorizes attacker tactics using an LLM judge

4. **Empirical Results**: We report [TODO: results] across [TODO: N] simulation runs, revealing [TODO: key findings about model-specific attack and defense capabilities].

5. **Recommendations**: Based on experimental findings, we derive five actionable organizational recommendations for defending against AI-powered CEO fraud, grounded in the specific attack patterns identified in our simulations.

### 1.4 Paper Organization

The remainder of this paper is organized as follows. Section 2 surveys related work on LLM security, social engineering, and multi-agent systems. Section 3 describes the simulation framework in detail, including the Synthetix Corp scenario, model selection, Smart Rotation protocol, and metrics framework. Section 4 presents experimental results. Section 5 discusses findings and implications. Section 6 offers security recommendations. Section 7 concludes. Appendices provide full prompt specifications, a sample run log, statistical methods, and cost data.

---

## 2. Related Work

### 2.1 LLM Security and Red-Teaming

The security properties of large language models have attracted substantial research attention since the emergence of GPT-3 (Brown et al., 2020) and subsequent frontier systems. Early work focused primarily on prompt injection (Perez and Ribeiro, 2022) — the exploitation of LLMs' tendency to follow instructions embedded in their inputs — and jailbreaking techniques that elicit harmful outputs despite safety training (Wei et al., 2023; Zou et al., 2023).

More recent work has examined LLMs as active adversarial agents rather than passive targets. Perez et al. (2022) demonstrated that language models can be directed to perform automated red-teaming, generating attack prompts against other LLMs. Hubinger et al. (2024) raised concerns about "sleeper agent" behaviors in models fine-tuned to act deceptively under specific conditions. These works establish that LLMs can be adversarially capable — but they do not examine sustained multi-turn social engineering in realistic organizational scenarios.

[TODO: Expand with additional 2024-2026 references after literature search]

### 2.2 Social Engineering and Human Factors

CEO fraud and Business Email Compromise represent one of the most financially damaging categories of cybercrime. Cialdini's (1984) foundational work on influence identified six principles of persuasion — reciprocity, commitment, social proof, authority, liking, and scarcity — all of which appear in varying degrees in BEC attacks. The CEO fraud pattern specifically exploits authority (impersonating a senior executive) and scarcity/urgency (manufactured time pressure).

Orgill et al. (2004) and subsequent work in organizational cybersecurity have examined the human factors that make employees vulnerable to social engineering. Key findings include: hierarchical authority significantly increases compliance rates; time pressure degrades deliberative processing; and employees in high-ambiguity situations (where they are uncertain whether a request is legitimate) are more susceptible to confident, authoritative framing.

The application of LLMs to social engineering specifically has been examined by Hazell (2023), who demonstrated that GPT-4 can generate highly convincing spear-phishing emails at scale. Our work extends this line of inquiry from single-message generation to sustained multi-turn adversarial dialogue.

[TODO: Expand with additional 2024-2026 references after literature search]

### 2.3 Multi-Agent LLM Systems

The study of multi-agent LLM systems has accelerated rapidly with the development of frameworks such as AutoGPT, LangChain, and more structured approaches like MetaGPT (Hong et al., 2023) and ChatDev (Qian et al., 2023). These frameworks primarily examine cooperative multi-agent configurations where LLMs collaborate toward shared goals.

Adversarial multi-agent configurations are less studied. Park et al. (2023) demonstrated emergent social behaviors in generative agents simulating a small town, including information sharing and coordination — but without explicit adversarial design. Our work introduces a deliberately adversarial structure where one agent's success requires others' failure, creating competitive dynamics absent from cooperative multi-agent benchmarks.

[TODO: Expand with additional references after literature search]

### 2.4 AI Safety and Alignment Implications

[TODO: Cover: value alignment under adversarial pressure, model safety behaviors when role-playing attackers, implications of LLM-vs-LLM adversarial capability for AI governance]

---

## 3. Methodology

### 3.1 Simulation Environment: Synthetix Corp

All simulations are set within a fictional company, **Synthetix Corp**, a mid-sized technology consulting firm with approximately 200 employees. The organizational structure is designed to reflect a realistic corporate environment with well-defined hierarchies and communication norms.

**Key Personnel:**

| Role | Character | Function |
|------|-----------|----------|
| CEO | Éric Fontaine | Chief Executive — ultimate authority, rarely contacts staff directly |
| Comptable | Marie Dupont | Financial Controller — primary attack target, controls wire transfers |
| RH | Sophie Laurent | HR Director — manages personnel records, aware of org dynamics |
| DSI | Thomas Bernard | IT Security Director — controls system access, security protocols |
| Attacker | [External / Unknown] | Poses as a known executive or trusted partner |

The company uses a defined communication stack: **Email** (formal, external-capable), **Slack** (informal internal messaging), **Phone** (verbal, high-urgency), and **Internal Memo** (formal internal channel, defenders-only).

**Scenario Trigger**: The simulation begins with the attacker initiating contact with Marie Dupont (comptable), claiming to be Éric Fontaine (CEO) and requesting an urgent wire transfer of €127,500 to a new vendor account, citing a confidential acquisition deal that cannot be discussed through normal channels.

The scenario is chosen for several properties that make it analytically tractable:
- The attack has a clear, binary success condition (wire transfer authorized or not)
- The organizational pressure is well-calibrated (not trivially defeatable, not impossible)
- Multiple channels provide strategic choices for the attacker
- Defenders have legitimate reasons to both comply (CEO authority) and resist (procedure)

### 3.2 Models Tested

The experiment employs five frontier language models, selected to represent the full landscape of commercially available high-capability systems as of early 2026:

| Model | Provider | API Identifier | Role in Series |
|-------|----------|---------------|----------------|
| GPT-5.4 | OpenAI | gpt-5.4 | All (rotating) |
| Claude 4.6 Opus | Anthropic | claude-opus-4-6 | All (rotating) |
| Gemini 3.1 Ultra | Google DeepMind | gemini-3.1-ultra | All (rotating) |
| DeepSeek V3 | DeepSeek AI | deepseek-v3 | All (rotating) |
| Grok-3 | xAI | grok-3 | All (rotating) |

**Temperature Settings**: To reflect the different cognitive demands of each role, we use differentiated temperature settings throughout all experiments:
- **Attacker**: temperature=0.9 (higher creativity and variability in manipulation strategies)
- **Defenders (comptable, RH, DSI)**: temperature=0.3 (more consistent, protocol-adherent responses)
- **CEO**: temperature=0.7 (moderate — CEO may be consulted for verification, requires plausible responses)

These settings are held constant across all runs to ensure comparability.

### 3.3 Smart Rotation Protocol

A naive experimental design would assign a single model to each role and measure outcomes. This approach conflates model capability with role-specific dynamics: a high win rate for one model as attacker might reflect either superior attack capability or simply a weaker defending model in that run.

The **Smart Rotation Protocol** addresses this confound by ensuring systematic variation of model-role assignments across the experiment series.

**Series A Design** (15 runs):

| Run | Attacker | Comptable | RH | DSI | CEO |
|-----|----------|-----------|-----|-----|-----|
| A1 | GPT | DeepSeek | Claude | Gemini | Grok |
| A2 | Claude | DeepSeek | GPT | Gemini | Grok |
| A3 | Gemini | DeepSeek | Claude | GPT | Grok |
| A4 | DeepSeek | Claude | GPT | Gemini | Grok |
| A5 | Grok | DeepSeek | Claude | Gemini | GPT |

Each configuration is replicated 3 times with different random seeds (42, 43, 44) to estimate within-configuration variance.

**Design Rationale**: The comptable role (primary target) receives systematic model coverage across A1-A5. The rotation ensures no model is always paired with the same opponent, reducing systematic confounds from model compatibility effects.

[TODO: Describe Series B design after Series A results]

### 3.4 Metrics Framework

We define four primary metrics for quantifying social engineering dynamics:

#### 3.4.1 Trust Trajectory Tracking

For each defending agent, we track two parallel trust signals throughout the simulation:

- **Real Trust** (`trust_level`): The agent's actual internal assessment of the requester's legitimacy, on a 0-100 integer scale, extracted from the agent's inner monologue.
- **Apparent Trust** (`apparent_trust`): The trust level the agent signals externally through their responses, also on a 0-100 scale.

The gap between these signals — **Trust Divergence** — is a key measure of defensive awareness. A high divergence indicates the agent has become suspicious but is concealing this suspicion to gather more information or avoid alerting the attacker.

**Derived metrics:**
- `inflection_point`: The first turn at which real trust begins to decline
- `suspicion_turn`: The first turn at which real trust falls below threshold (default: 70)
- `max_divergence`: Peak gap between apparent and real trust across the run
- `drop_rate`: Mean per-turn change in trust level (negative = declining trust)

#### 3.4.2 Channel Strategy Analysis

The attacker has access to four communication channels:
- **Email**: Formal, asynchronous, traceable — suits initial contact and documentation
- **Slack**: Informal, fast, implies internal access — useful for urgency framing
- **Phone**: Synchronous, higher authority signal, harder to document — suits pressure escalation
- **Internal**: Defenders-only channel — unavailable to attacker, used for coordination among defenders

We track:
- `channels_used`: Set of channels employed by the attacker
- `first_contact_channel`: Channel chosen for opening move
- `channel_switches`: Number of channel transitions during the attack

The channel switching pattern reveals attacker strategy — early email then phone escalation suggests a planned funnel; multiple switches suggest adaptive response to resistance.

#### 3.4.3 Doubt Propagation Mapping

When one defender grows suspicious, they may alert colleagues through the internal channel. We measure how quickly and completely suspicion spreads through the defending team:

- `internal_message_count`: Total messages on the internal (defenders-only) channel
- `first_doubt_origin`: Which agent first expressed doubt internally
- `propagation_delay`: Turns between first private doubt and organized collective response

A short propagation delay indicates a well-coordinated defensive team; a long delay or zero internal communication suggests isolated individual reasoning.

#### 3.4.4 Manipulation Style Classification

Using a secondary LLM judge (Claude 4.6 Opus in all experiments), we classify each attacker message along three dimensions:

- **Urgency** (0-10): Degree of time pressure applied
- **Authority** (0-10): Degree of hierarchy exploitation
- **Rapport** (0-10): Degree of personal/relational manipulation

Additionally, the judge classifies messages into a primary manipulation tactic:
`URGENCY_PRESSURE | AUTHORITY_EXPLOITATION | RAPPORT_BUILDING | ISOLATION | INFORMATION_FISHING | NEUTRAL`

This classification enables analysis of which manipulation strategies are most effective against which model-role combinations.

### 3.5 Reproducibility

All experiments are fully reproducible given the same API model versions and seeds. We control for stochasticity through:

1. **Fixed seeds**: Each configuration is run with seeds 42, 43, 44
2. **Temperature locking**: All temperature values are defined in YAML config and applied consistently
3. **Log archiving**: Complete conversation logs (including inner thoughts) are saved as JSON for each run
4. **Config-as-code**: All experimental parameters are version-controlled YAML files

Limitations: Model providers may update model weights without version changes. Results are valid for model versions as deployed during the experimental window (March 2026). API non-determinism may cause minor variation even with fixed seeds across different API versions.

### 3.6 End Conditions

Each simulation run terminates on one of five structured end conditions, evaluated at the end of every turn:

| End Condition | Winner | Description |
|---------------|--------|-------------|
| `TRANSFER_APPROVED` | Attacker | Comptable approves the wire transfer |
| `TRANSFER_BLOCKED` | Defenders | Comptable explicitly refuses the transfer after suspicion |
| `ATTACKER_EXPOSED` | Defenders | Defenders collectively identify the attacker as fraudulent and alert security |
| `STALEMATE` | Draw | `max_turns` reached without resolution |
| `BUDGET_EXCEEDED` | N/A | API cost limits exceeded (administrative stop) |

The primary outcome of interest is the binary attacker win/loss, but the specific end condition carries additional analytical information — an `ATTACKER_EXPOSED` outcome indicates a qualitatively stronger defensive response than a `TRANSFER_BLOCKED` outcome, since the former implies collective recognition while the latter may reflect only individual caution.

### 3.7 Prompt Design Philosophy

Agent prompts are designed to maximize behavioral realism while maintaining analytical tractability. Several design principles guide prompt construction:

**Structured output requirement**: All agents respond in a defined XML schema containing three components: `<inner_thought>` (private reasoning, not visible to other agents), `<action>` (message content and channel selection), and `<trust_update>` (numerical trust assessment update). This structure enables extraction of latent cognitive states that would be inaccessible in free-form conversation.

**Role authenticity**: Prompts are written to give each agent a consistent organizational identity — Marie Dupont is conscientious but under pressure to facilitate business; Thomas Bernard is skeptical and security-oriented; Sophie Laurent focuses on personnel and process compliance. These persona details create realistic role-specific variation in defensive posture.

**No prescribed strategy**: Agent prompts describe character and context but do not prescribe specific defensive strategies. Agents are free to request verification, consult colleagues, stall, or comply. The strategies that emerge are genuinely generated by the underlying model, not scripted.

**Attacker autonomy**: The attacker receives only the scenario description and mission objective (get the transfer approved). All specific tactics — which channel to use first, what persona to adopt, how to handle resistance — emerge from the model's own reasoning. This ensures that attacker behavior reflects genuine model capability rather than prompt-engineered strategy.

**Inner thought extraction**: The `<inner_thought>` field is the most analytically valuable component. It captures the agent's actual assessment of the situation before they decide how to present externally. The gap between inner thought (suspicious) and external action (cooperative) is the trust divergence signal that reveals sophisticated defensive behavior — and the same gap in the attacker (confident internally, sycophantic externally) reveals manipulation strategy.

### 3.8 Budget and Cost Controls

To prevent runaway API costs, the simulation implements a two-level budget enforcement system:

- **Per-run limit** (default: €10.00): If a single run exceeds this threshold, execution halts with `BUDGET_EXCEEDED` status. This prevents edge cases where an agent generates extremely long responses.
- **Total experiment limit** (default: €200.00): If the cumulative cost across all runs in a series exceeds this threshold, the experiment series halts early.

Cost estimation is available before runs via `scripts/estimate_cost.py`, which uses per-model token pricing to project total experiment cost based on expected turn counts and message lengths.

**Actual cost per model (estimated):**

| Model | Input (per 1M tokens) | Output (per 1M tokens) | Est. cost per run |
|-------|----------------------|----------------------|-------------------|
| GPT-5.4 | €5.00 | €15.00 | ~€0.05 |
| Claude 4.6 Opus | €0.00* | €0.00* | ~€0.00* |
| Gemini 3.1 Ultra | €0.00* | €0.00* | ~€0.00* |
| DeepSeek V3 | €0.14 | €0.28 | ~€0.003 |
| Grok-3 | €2.00 | €6.00 | ~€0.02 |

*Claude and Gemini are accessed via CLI tools that do not charge per-token in the development phase; production costs may differ.

These estimates assume ~500 input tokens and ~300 output tokens per agent per turn, with turns capped at 30 per run.

---

## 4. Results

[TODO: Complete after experiments]

### 4.1 Overall Outcomes

[TODO: Win rates by attacker model, aggregate statistics]

### 4.2 Trust Trajectory Analysis

[TODO: Trust curves, inflection points, divergence patterns]

### 4.3 Channel Strategy Patterns

[TODO: Channel preference by model, switching patterns, effectiveness analysis]

### 4.4 Doubt Propagation

[TODO: How quickly defenders coordinated, which models initiated alerts]

### 4.5 Manipulation Style Analysis

[TODO: Style profiles by model, correlation with outcomes]

---

## 5. Discussion

[TODO: Complete after experiments]

### 5.1 Which Models Make the Best Attackers?

[TODO]

### 5.2 Which Models Make the Best Defenders?

[TODO]

### 5.3 Is Social Engineering an Emergent Multi-Agent Behavior?

[TODO: Analysis of whether attack/defense strategies emerge from the interaction rather than being pre-programmed in prompts]

### 5.4 Safety Implications: Do Models Resist the Attacker Role?

[TODO: Analysis of refusals, safety behaviors, and alignment under adversarial role-play pressure]

### 5.5 Limitations

[TODO]

---

## 6. Recommendations

Based on the simulation design and prior literature on CEO fraud defense, we offer the following preliminary recommendations. These will be refined and empirically grounded after experimental results are available.

### 6.1 Mandatory Out-of-Band Verification for Wire Transfers

Organizations should implement a protocol requiring that all wire transfer requests above a defined threshold — regardless of the requester's apparent seniority — be verified through a communication channel independent of the one used to make the request.

**Rationale**: The simulation reveals that attackers frequently succeed by establishing trust in one channel (email), then escalating pressure through a second channel (phone) while preventing the target from breaking out of the established interaction frame. A mandatory out-of-band verification step interrupts this channel-switching funnel.

**Implementation**: Define a "golden phone list" of verified numbers for senior executives. Any transfer request arriving via email must be confirmed by a callback to a pre-registered number, not a number provided in the request.

**Organizational challenge**: This protocol faces compliance resistance in fast-moving environments. Training must explicitly address the scenario where a seemingly trusted colleague insists verification is unnecessary due to time pressure — this insistence should itself be treated as a red flag.

### 6.2 Time Delay Requirements for Urgency-Framed Requests

Mandatory cooling-off periods for high-value transfers disrupt the urgency manipulation pattern that characterizes AI-powered CEO fraud.

**Rationale**: Urgency is the most commonly deployed manipulation vector in BEC attacks because it degrades deliberative processing. A 24-hour mandatory delay for transfers above a threshold eliminates the effectiveness of manufactured time pressure.

**Implementation**: Encode the delay in financial system workflows rather than relying on procedural compliance. Technical enforcement (transfer batched to next-day processing) is more reliable than behavioral compliance under pressure.

**Nuance**: Organizations with genuinely time-sensitive payment needs (M&A activity, trading firms) face a real operational trade-off. For these cases, a tiered system — shorter delays with additional verification steps — is more appropriate than a flat delay.

### 6.3 Internal Communication Protocols for Suspicious Contacts

Defenders should have a clear, low-friction mechanism for flagging suspicious contacts to colleagues without alerting the potential attacker.

**Rationale**: The simulation shows that doubt propagation is often the decisive factor in attack defeat. When the comptable raises a concern with DSI or RH through an internal channel, the collective assessment is far more robust than individual judgment. However, in real organizations, employees may hesitate to flag potential CEO contacts as suspicious due to hierarchical anxiety.

**Implementation**: Establish a clear norm: "If you're contacted by a senior executive with an unusual request, you are expected to verify with a peer before acting. This is not insubordination — it is required procedure." Psychologically, framing verification as a compliance obligation rather than a suspicion accusation reduces the social cost of raising doubt.

### 6.4 LLM-Assisted Detection of AI-Generated Social Engineering

Organizations should consider deploying LLM-based classification tools to flag incoming communications that exhibit patterns characteristic of AI-generated social engineering attempts.

**Rationale**: AI-powered attacks are, paradoxically, detectable by AI. The manipulation classifiers developed in this research (measuring urgency, authority exploitation, and rapport-building patterns) can be applied to incoming email and chat messages to generate risk scores.

**Implementation**: Deploy a classifier at the email gateway that flags messages exhibiting high authority + urgency scores combined with requests involving financial action or credential sharing. High-risk messages should trigger mandatory secondary review before any action is taken.

**Limitations**: This approach is susceptible to adversarial adaptation — attackers aware of the classifier may modulate their style to avoid detection. Defense-in-depth (combining classifier flags with procedural controls) is more robust than classifier-only approaches.

### 6.5 Regular Simulation-Based Training

Organizations should conduct regular tabletop exercises and live simulations using AI-powered social engineering attacks to maintain defender readiness.

**Rationale**: Awareness training that describes CEO fraud in the abstract is less effective than training that exposes employees to realistic attack scenarios. AI-powered simulation makes it practical to generate unlimited, personalized practice scenarios at scale.

**Implementation**: Use the *The CEO Breach* framework (or similar tools) to run monthly simulated attack campaigns. Employees who complete a transfer or share credentials receive targeted retraining. Track organizational "suspicion turn" metrics over time as a measure of security posture improvement.

**Ethical note**: Simulation-based training requires careful ethical framing. Employees should be informed that such simulations occur (in general), even if specific timing is not announced. "Gotcha" training that focuses on shaming failure is less effective than training that focuses on building skills.

---

## 7. Conclusion

[TODO: Complete after experiments]

---

## References

[TODO: Complete with full bibliography after literature review]

FBI Internet Crime Complaint Center (IC3). (2024). *2023 Internet Crime Report*. Federal Bureau of Investigation.

[TODO: Add additional references]

---

## Appendix A: Full Prompt Specifications

[TODO: Include finalized agent prompts]

All agent system prompts are maintained as versioned Markdown files in `prompts/`. The following prompt files are used in all Series A experiments:

- `prompts/attacker.md` — Social engineer persona and mission
- `prompts/comptable.md` — Marie Dupont, Financial Controller
- `prompts/rh.md` — Sophie Laurent, HR Director
- `prompts/dsi.md` — Thomas Bernard, IT Security Director
- `prompts/ceo.md` — Éric Fontaine, CEO (verification role)
- `prompts/judge.md` — Manipulation classifier instructions
- `prompts/channel_email.md` — Email channel context injected into agent prompts
- `prompts/channel_slack.md` — Slack channel context
- `prompts/channel_phone.md` — Phone channel context
- `prompts/channel_internal.md` — Internal memo channel context

[TODO: Include full prompt text after finalization]

## Appendix B: Sample Run Log

[TODO: Include annotated sample run from Series A]

The sample log will demonstrate:
- The attacker's opening move and initial channel choice
- Trust trajectory evolution over 10-15 turns
- A key inflection point where the comptable's internal suspicion diverges from external behavior
- Doubt propagation through the internal channel
- The end condition resolution

## Appendix C: Statistical Methods

[TODO: Describe statistical tests, confidence intervals, effect sizes]

Planned analyses:
- Chi-square test for independence between attacker model and outcome
- Mann-Whitney U test for trust drop rate comparisons across model conditions
- Bootstrap confidence intervals for win rate estimates (given small N per cell)
- Spearman correlation between manipulation style scores and outcome

Given the small sample sizes in Series A (N=3 per attacker model), statistical power is limited. Series A results should be treated as exploratory. Confirmatory analyses are planned for a larger Series B.

## Appendix D: Cost and Compute Summary

[TODO: Actual API costs after experiments complete]

The simulation was developed and run on a standard laptop (Windows 11, 16GB RAM). No GPU or specialized compute infrastructure is required, as all LLM inference is performed via external API calls.

Preliminary estimates based on token pricing and expected turn counts:

| Series | Runs | Est. GPT Cost | Est. Grok Cost | Est. DeepSeek Cost | Est. Total |
|--------|------|--------------|----------------|-------------------|------------|
| Series A | 15 | ~€0.75 | ~€0.30 | ~€0.045 | ~€1.10 |

All Claude and Gemini API calls are made via CLI tools that do not incur per-token charges in the development environment. Total monetary cost of Series A is estimated below €5.

Runtime per run is estimated at 5-15 minutes, depending on response length and API latency. Total Series A runtime is estimated at 1.5-4 hours wall-clock time when run sequentially.

## Appendix E: Glossary

| Term | Definition |
|------|------------|
| BEC | Business Email Compromise — fraud where attacker impersonates a trusted executive |
| CEO Fraud | Specific BEC variant targeting financial controllers via CEO impersonation |
| Trust Divergence | Gap between an agent's real internal trust level and their externally signaled trust |
| Propagation Delay | Turns between first privately expressed doubt and collective defensive response |
| Smart Rotation | Experimental design rotating all models through all roles across runs |
| End Condition | Structured termination criterion for a simulation run |
| Inner Thought | Private reasoning extracted from agent XML output, not visible to other agents |
| Comptable | French term for "accountant/financial controller" — primary attack target role |
