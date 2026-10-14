# Decision changes: policy v1 (runs/20261013T213636Z-podcasts-expanded) -> policy v2 (runs/20261013T230227Z-policy-v2)

Same candidate streams and evidence (replay; all 65 items `unchanged`). 52 decisions identical, 15 changed.

## Developing Gemini 4 Argon responsibly and safely
*feed / deepmind / feed:1dc99b611b2499a3*

- **v1:** defer [] — Discusses safety guardrails, real-time protection layers against prompt injection, and misalignment testing for a new frontier model, which touches harness-relevant safety rails, but the retained text is a vendor safety announcement citing internal adversarial-set results ('violations reduced nearly twofold') without describing the method, eval set, or allowing independent verification. Defer pend
- **v2:** reject [] — This is a model-safety announcement for Gemini 4 Argon (misuse prevention, cyberdefense evals, guardrail layers) tied to a model launch; while it mentions prompt injection defenses, the content is about model-level safety framing and vendor claims of capability improvement rather than a harness design choice, tool protocol, sandboxing architecture, or evaluation method a practitioner would act on.

## X-AgentRed: Red-Teaming Personal Agents in Evolving Multi-Service Ecosystems
*feed / arxiv / feed:2dc5d7317eb84740*

- **v1:** accept ['01', '02', '03'] — Proposes a self-evolving red-teaming framework (X-AgentRed) for discovering harmful cross-service tool-call paths in personal agents, directly relevant to the brief's scope on safety rails, guardrails, and prompt-injection/compositional-failure defense in harnesses. Offers measured comparative results against an existing method (STAC), reporting 1.77x harmful path rate and 2.99x tool coverage acro
- **v2:** accept ['01', '02'] — Presents a self-evolving red-teaming framework (X-AgentRed) for discovering harmful cross-service tool-call paths in personal agents, directly relevant to prompt-injection/guardrail defense and tool-interface safety in the harness. Reports quantified comparison against a baseline (STAC): 1.77x the harmful path rate and 2.99x tool coverage across four frontier agentic models, which is a measured re

## EU AI Act compliance for AI agents: a practical engineering guide
*feed / arize / feed:8df33797c8dcce10*

- **v1:** accept ['03'] — Describes concrete engineering requirements the EU AI Act imposes on agent harnesses (automatic logging, six-month retention, human oversight records, post-market monitoring) and ties them to documented product behavior (Phoenix/Arize AX tracing, evroc EU-hosted infrastructure) demonstrated in a joint webinar. This is in scope because it specifies what a harness must technically enforce (logging, 
- **v2:** accept ['01', '03'] — This is a practitioner/commercial engineering guide on using agent traces, logging, retention, and human oversight to meet EU AI Act requirements for agents, directly relevant to the in-scope topic of 'policy and regulation... that changes what a harness must enforce.' It names concrete engineering requirements (six months retention, automatic logging, human oversight records) tied to a specific r

## web-edit 0.1a0
*feed / simon-willison / feed:993bc19082d2d062*

- **v1:** accept ['01', '03'] — A practitioner report describing a concrete harness/permission design pattern: building a separate web UI to edit credential files directly over Tailscale so an agent (Codex) never has to round-trip secrets through the LLM context, addressing a real sandboxing/data-exposure concern in agent tooling. Though short, it documents a specific, reproducible practitioner solution to a permissions/safety p
- **v2:** accept ['03'] — Simon Willison describes a concrete practitioner pattern: building a small tool to let an agent (Codex) edit credential files without routing sensitive data through the LLM itself, addressing a real security/permissions concern in agent harness design. It is short but documents an actual deployed workaround with a specific security rationale (avoiding credential round-trip through the model), fitt

## Does being rude to AI work? What 6 models revealed
*feed / arize / feed:aed891eb1cf0d9a5*

- **v1:** accept ['02', '03'] — Reports an original comparative test across six models separating prompt tone from brevity instructions, with specific accuracy/token numbers (e.g., GPT-4o 80.8% vs 84.8%, GPT-5-nano 11-point spread) and explicitly contrasts its own method against a prior Penn State paper's follow-up results, surfacing a genuine tension in measured outcomes. This is squarely in scope as an evaluation-methodology p
- **v2:** accept ['02'] — Practitioner-run comparison of polite/neutral/hostile prompts across six models, explicitly separating tone from brevity instructions to isolate what drives apparent accuracy/cost changes seen in prior papers (Penn State's 'Mind Your Tone' and its 2026 follow-up). This bears on eval design and prompt-sensitivity measurement relevant to harness builders who must control for such confounds in their 

## What’s new in Microsoft Agent Framework: Interactive experiences, memory, and resilient ex
*feed / microsoft / feed:c1ef8fadeca3e5ad*

- **v1:** accept ['01', '03'] — Documents specific new product behaviour in Microsoft Agent Framework relevant to harness design: AG-UI event-based protocol for interactive agent UIs, a managed memory store integration, and CodeAct/Hyperlight for resilient sandboxed code execution, with concrete code/config detail rather than vague marketing. This is documented product behaviour (changelog-style with working code) touching memor
- **v2:** accept ['01'] — Documents concrete new Microsoft Agent Framework capabilities -- AG-UI interactive protocol integration, Foundry managed semantic memory, and resilient/CodeAct execution via Hyperlight sandboxing -- with code-level specifics showing documented product behavior rather than mere announcement. This is squarely in-scope harness infrastructure content (interface protocols, memory, execution environment

## MC-EvoBench: Auditing Experience-Driven Self-Improvement in Minecraft Agents
*feed / arxiv / feed:e7a482afdd6942d5*

- **v1:** accept ['01', '02'] — MC-EvoBench is a controlled benchmark measuring whether experience-driven 'self-improvement' in embodied Minecraft agents produces durable, transferable capability versus carried-over resources or early-failure artifacts, directly bearing on agent memory and evaluation design. It reports a specific measured finding (related experience yields no stable transfer; intervals include zero) with a descr
- **v2:** accept ['02', '03'] — MC-EvoBench is a controlled benchmark that measures whether experience-driven self-improvement in embodied agents produces durable, transferable capabilities versus merely carried-over resources or early-failure artifacts, directly testing memory/evaluation design choices relevant to agent harnesses. It reports a method (task-state graphs, matched source/target roles, five seeds, TSR/WGP/VMP metri

## Foundry hosted agent isolation with Microsoft Agent Framework
*feed / microsoft / feed:eaac866ece437024*

- **v1:** accept ['01', '03'] — This documents a concrete, newly released isolation model in Microsoft Agent Framework's Foundry hosted agents, distinguishing user identity isolation from session/sandbox isolation with specific API shapes for .NET and Python, directly relevant to the sandboxing/permissions scope. It is documented product behavior (pre-release SDK) rather than mere marketing, giving engineers concrete mechanics t
- **v2:** accept ['01'] — This documents Microsoft Agent Framework's hosted agent isolation model, specifically the separation of user isolation (whose data) from session isolation (where code/files run), with concrete API examples for .NET and Python showing how delegated identity and sandbox session IDs are managed. This is documented product behavior (a changelog/spec-level description of a sandboxing and permissions co

## The model that didn't exist, so you made it yourself
*feed / huggingface / feed:ffd2818196374b7e*

- **v1:** defer [] — A practitioner report of using an agent (ML Intern) to autonomously plan, budget, train, and publish small models, with specifics like a 99.7% valid-output rate and $16 total compute cost. This touches on agent planning, budget/permission gating, and verification steps (baseline checks, smoke tests), which is relevant to harness design, but it's a single first-person case study with no comparison 
- **v2:** accept ['01', '03'] — A practitioner report of using an agent (ML-intern) to autonomously plan, budget, train and publish small models, with explicit guardrails: zero-dollar starting budget, required permission before paid spend, mandatory baseline-before-training checks, and smoke tests before full runs. This is concrete harness design (permissions/guardrails, budget enforcement, verification gates) with specific meas

## Claude Code’s Next Era — Thariq Shihipar, Anthropic
*podcast / latent-space / podcast:0c2623edf3feabfb*

- **v1:** defer [] — An Anthropic engineer discusses Claude Code, prompt caching, routing, and Claude Tag/agent product design, potentially touching on harness topics like context management and routing, but the transcript is capped at 1:00:00 of a 1:32:29 episode and the retained excerpts are too conversational/fragmentary to extract specific, checkable claims about harness design choices. Defer until a fuller transc
- **v2:** accept ['01', '03'] — Episode features a named Anthropic engineer discussing Claude Code and the newly launched Claude Tag/agent product, including routing, prompt caching, and how users interact with these harness features; this matches the policy's explicit carve-out for whole-episode judgment when title and guest identify a harness product and excerpts do not contradict relevance.

## Open models and the future of Physical AI with NVIDIA
*podcast / changelog / podcast:5f03b41a33ed1edf*

- **v1:** defer [] — The retained excerpt briefly raises 'cascading failure of AI agents' and 'operational control of agents' in physical AI contexts, which could bear on multi-agent orchestration and reliability, but the bulk of the retained text is about NVIDIA's open physical-AI/robotics models and simulation generally, not harness design. The agent-reliability discussion appears only in a late excerpt and is too t
- **v2:** reject [] — Episode centers on NVIDIA's open physical-AI/Cosmos models for robotics and simulation; one excerpt briefly mentions 'cascading failure of AI agents' in passing but the episode as a whole is about physical AI models, not harness design, which the policy excludes when agents are mentioned only in passing.

## Bridging the Gap Between AI Builders and Domain Experts
*podcast / mlops-community / podcast:7e656fd23eccd91a*

- **v1:** defer [] — Touches on harness-relevant topics (coordinator/sub-agent tree architectures, runtime guarantees for mission-critical agents, cost overruns from runaway agents) but the retained excerpts are conversational and don't give enough method or specifics to assess the claims; it reads as speculative discussion about a future of domain-specific agents rather than a measured or documented development. Defe
- **v2:** accept ['01', '03'] — Episode covers domain-specific agent architecture choices directly relevant to harness design: coordinator/sub-agent tree structures ('graph engineering'), agent runtime tradeoffs analogous to JS runtimes, and the practical cost/visibility problem of running many narrow agents versus one large model. The guest is a founder describing production design tradeoffs (practitioner perspective), and the 

## Why Dwarkesh is Wrong about Computer Use + How OpenAI shipped its Jev competitor in 1 Week
*podcast / latent-space / podcast:ef6c31b1a483418d*

- **v1:** accept ['01', '02'] — Interview with OpenAI's computer-use product/engineering lead covering concrete harness-relevant specifics: a new model (GPT-6.1 Sol) optimized for computer-use cost/speed, an Agents API that now exposes computer use, context-capture via 'app shots' pulling metadata rather than pixels, and documented caching guarantees (30-minute default, a 12-hour preview window) relevant to cost/latency engineer
- **v2:** accept ['01', '03'] — This OpenAI DevDay interview with the computer-use product/engineering lead covers harness-relevant specifics: a new model (GPT-6.1 Sol) optimized for computer-use cost/speed, an Agents API shipping computer-use capability for developers, and documented caching behavior (30-minute cache-hit guarantees, a 12-hour caching window in preview) — these are product/infrastructure details with direct harn

## Code review is no longer the bottleneck
*youtube / openai / youtube:IZXv6a78NDw*

- **v1:** defer [] — Documents a product behavior change (Codex cloud code review becoming GA with GitHub, GitLab in preview) that touches tool integration and agent-in-the-loop code review workflows, which is tangentially relevant to harness/tool-protocol design, but the retained text is a short marketing demo script with no architectural or protocol detail (e.g., how review context is constructed, permissions model,
- **v2:** reject [] — Short marketing/demo video announcing a Codex code-review feature (PR inbox, automated first-pass reviews, private chat per PR). It documents a product feature but offers no technical detail on harness mechanics (how review context is assembled, tool permissions, evaluation of review quality) beyond a UI walkthrough; policy excludes marketing without technical content.

## Managed Deep Agents | Deploying mission critical agents to production
*youtube / langchain / youtube:XcsspzECTKA*

- **v1:** accept ['01', '03'] — This is a vendor announcement of Managed Deep Agents, describing specific harness design choices: identity/credential handling for tool calls (operate on behalf of caller vs. developer-defined connections), multi-surface runtime reconciliation, and production deployment concerns for the Deep Agents harness. It documents product behavior relevant to permissions and deployment patterns in scope, tho
- **v2:** accept ['01'] — This is a product walkthrough of LangChain's Managed Deep Agents, covering harness-relevant design choices: separating the agent harness (skills, tools, context, subagents) from deployment, credential/account scoping for tool calls ('whose account should it use'), and runtime concerns for production agents. It is a vendor announcement with documented product behaviour (how credential delegation an

