# First final live run → second live run

Comparison: `20261013T213636Z-podcasts-expanded` → `20261014T014037Z-second-live`.

All 67 extracted observations were unchanged relative to the persistent store at the start of the second run (0 new, 0 changed). The eligible corpus grew from 67 to 73 because intervening runs had already stored additional evidence, including the labelled injected item. This is not 6 new discoveries in the second run. The date window advanced one UTC day and policy v2 replaced v1. Selection is also stochastic; differences cannot be attributed to policy alone.

24 items have changed/new decisions or piece assignments; 73 decisions total. First run: 27 accept / 33 reject / 7 defer. Second run: 27 accept / 45 reject / 1 defer.

## Developing Gemini 4 Argon responsibly and safely
`feed:1dc99b611b2499a3`

- Before: defer []
- After: reject []
- Reason: This is a vendor safety-and-responsibility announcement for a new model (Gemini 4 Argon) covering misuse prevention and alignment at the model level, not harness engineering; it mentions 'guardrails' and 'prompt injection' only in the context of model-level red-teaming and real-time protection layers Google built around the model itself, not reusable harness patterns practitioners can apply. Per scope, model launches and their associated safety reports are excluded absent a specific harness-design implication, and the claims here (e.g., 'violations reduced nearly twofold') are vendor-asserted without an independently described method accessible to practitioners.

## X-AgentRed: Red-Teaming Personal Agents in Evolving Multi-Service Ecosystems
`feed:2dc5d7317eb84740`

- Before: accept ['01', '02', '03']
- After: accept ['01', '02']
- Reason: X-AgentRed presents a self-evolving red-teaming framework for personal agents that builds a tool-dependency graph to discover harmful cross-service action paths, directly relevant to prompt-injection/guardrail defense and agent safety evaluation in the harness. It reports measured comparative results against a named baseline (STAC): 1.77x the harmful path rate and 2.99x the tool coverage across four frontier agentic models, making it a new, well-specified research development in scope for safety rails and evaluation.

## llm-meta-ai 0.2
`feed:5ca8d6f055cb2e9f`

- Before: absent from first eligible corpus
- After: reject []
- Reason: A short practitioner note about updating a plugin to support Meta's new Muse Wonder model, with pelican-drawing comparisons as an informal capability test. This is a model-release reaction with no harness, tool-protocol, or agent-infrastructure content, falling under the exclusion for model launches without harness implication.

## llm-gemini 0.35
`feed:6451d923eed6bbe6`

- Before: absent from first eligible corpus
- After: reject []
- Reason: Covers pricing and informal pelican-SVG quality tests for the new Gemini 4 Argon model, plus a passing mention that 'what really matters is how many tokens a model takes to achieve a goal within an agentic harness' citing Artificial Analysis's aggregate benchmark cost. This touches cost-per-task but offers no harness design detail, method, or practitioner workflow change; it is a model-release reaction excluded per scope (model launches without harness implication).

## I expect rapid progress but not towards general superintelligence
`feed:720d85217c3c2ee6`

- Before: absent from first eligible corpus
- After: reject []
- Reason: This is general commentary on AI research-vs-engineering trajectories and superintelligence timelines, with no harness design, tool protocol, sandboxing, memory, evaluation, or production-operation content. It falls squarely under the brief's exclusion of general AI commentary with no harness implication.

## Redesigning source control at Anthropic
`feed:7e289d45dfc4cd8f`

- Before: absent from first eligible corpus
- After: accept ['01', '03']
- Reason: Reports documented engineering behavior directly relevant to the harness audience: Anthropic's internal code-change velocity rose from ~2,500 to 30,000+ merges/day driven by Claude-based coding agents, prompting a custom source-control system (Scion) built for agent-scale checkout volume (25M/day) and an adversarial-review practice with a described failure mode (myopic over-engineering in response to hypothetical concerns). This is new, specific documented-system reporting published this month that bears on production infrastructure for agentic coding at scale, fitting piece 01 (what changed) and 03 (implications for infra builders).

## Matched-Context Group Policy Optimization for LLM Agent Training
`feed:89a6239a0ab19877`

- Before: accept ['02']
- After: reject []
- Reason: Proposes a new RL training algorithm (MCGPO) for credit assignment in long-horizon LLM agents, with measured gains on ALFWorld/WebShop benchmarks (e.g., 0.47-5.16 percentage points over GraphGPO baselines). This is model-training methodology research rather than harness design, context management, tool protocols, sandboxing, memory, or production operation; it does not measure a harness design choice as scoped by the brief, so it falls outside the publication's focus on the agent harness layer.

## Profiling web-edit with Python 3.15: flame graphs and source heatmaps
`feed:97e3cba45007401f`

- Before: absent from first eligible corpus
- After: reject []
- Reason: This is a short post about profiling a personal Python web app (web-edit) with Python 3.15's new profiler, reporting CPU flame-graph findings about line-ending handling performance. It has no connection to agent harness design, tool protocols, evaluation, or orchestration; the agent angle (GPT-6 Astra in Codex) is incidental tooling used to run the profiler, not a harness development. Out of scope per policy: material that mentions agents only in passing.

## web-edit 0.1a0
`feed:993bc19082d2d062`

- Before: accept ['01', '03']
- After: reject []
- Reason: Announces a small personal web app (web-edit) built with Codex to edit files over Tailscale without piping credentials through an LLM. While mildly relevant to agent tool-use design (avoiding sensitive data round-tripping through a model), the post is a few paragraphs of release notes with no method, measurement, or generalizable harness lesson; it reads as a personal tool announcement, not engineering analysis. Falls under exclusion for short, marketing-free but substance-free posts with no harness implication beyond incidental agent use.

## [AINews] TypeSafe/Jev at >$100M ARR, $7.5B valuation 3 weeks after launch
`feed:99e1782a514f91f4`

- Before: reject []
- After: defer []
- Reason: This is an AINews link-roundup covering many items (decision-model APIs, funding valuations, routing cost claims) secondhand via social media posts; per policy roundups are secondary reporting and should be deferred unless no primary source exists. One harness-relevant thread (routing cheap models for yes/no agent steps, LangChain's claim of 64% cost cut on Open SWE) is attributed only to a tweet, not a primary source with method, so it cannot be verified from this text. Defer pending a primary source for the routing/decision-model cost claims.

## Does being rude to AI work? What 6 models revealed
`feed:aed891eb1cf0d9a5`

- Before: accept ['02', '03']
- After: reject []
- Reason: This is a prompt-tone/politeness experiment (does rudeness improve accuracy or reduce tokens) rather than harness engineering: it touches context, memory, tool protocols, sandboxing, eval infra, or production operation only tangentially. It references Anthropic's usage-policy change on cruelty toward models as a news hook but the harness-relevant content is thin generic prompt engineering, which the policy explicitly excludes.

## MC-EvoBench: Auditing Experience-Driven Self-Improvement in Minecraft Agents
`feed:e7a482afdd6942d5`

- Before: accept ['01', '02']
- After: accept ['02', '03']
- Reason: This is a research benchmark (MC-EvoBench) that measures whether experience-driven self-improvement in embodied agents produces durable, transferable capabilities versus carried-over artifacts, directly relevant to agent memory and evaluation design. It reports a measured method (19 evolution chains, matched budgets, five seeds, TSR/WGP/VMP metrics) and a concrete negative finding: related experience does not yield stable transfer and confidence intervals include zero, which is a harness-relevant evaluation result rather than a leaderboard score. This bears on how practitioners should evaluate memory/experience persistence claims in agent systems.

## Foundry hosted agent isolation with Microsoft Agent Framework
`feed:eaac866ece437024`

- Before: accept ['01', '03']
- After: accept ['01']
- Reason: This documents a specific sandboxing/permissions design in a shipping product: Microsoft Agent Framework's Foundry hosted agent isolation separates user identity isolation from session (sandbox compute/files) isolation, with concrete API examples for .NET and Python showing how delegated identities map to VM-isolated sandboxes. This is documented product behaviour squarely in the sandboxing/permissions scope the policy prioritizes, though it is a vendor-authored changelog-style post so its claims are presented as documented behaviour rather than independent measurement.

## The model that didn't exist, so you made it yourself
`feed:ffd2818196374b7e`

- Before: defer []
- After: reject []
- Reason: This is a first-person account of using Hugging Face's 'ML Intern' agent to distill small models, with details on prompting structure, budget caps, and smoke tests, but the core content is about prompt-engineering craft and model distillation workflow rather than harness design (context management, tool protocols, sandboxing, memory, eval infrastructure, or orchestration). It mentions a spend-cap/permission mechanism in passing but the piece's substance is about getting good distilled models cheaply, which falls under the brief's exclusion of general AI/model-training commentary without a harness implication.

## Claude Code’s Next Era — Thariq Shihipar, Anthropic
`podcast:0c2623edf3feabfb`

- Before: defer []
- After: accept ['01', '03']
- Reason: Episode features Thariq Shihipar, an early Anthropic Claude Code engineer, discussing Claude Code's evolution, agent design choices, prompt caching, and routing decisions -- squarely a harness-design conversation per the policy's whole-episode judgement rule for audio when title/guest/description identify harness content and excerpts don't contradict. Excerpts on prompt caching, routing per-query, and the complexity of Claude Code's agent paradigm are directly relevant to context/tool design discussions this publication covers.

## Open models and the future of Physical AI with NVIDIA
`podcast:5f03b41a33ed1edf`

- Before: defer []
- After: reject []
- Reason: Episode covers NVIDIA's open physical-AI models (Cosmos) and robotics/simulation topics; one excerpt briefly mentions 'cascading failure of AI agents' and 'operational control of agents' but only in passing, not as sustained harness engineering content. This is primarily about physical AI/robotics model development, not agent loop, tool protocol, or production-operation engineering, so it falls under the exclusion for material that mentions agents only in passing.

## Bridging the Gap Between AI Builders and Domain Experts
`podcast:7e656fd23eccd91a`

- Before: defer []
- After: accept ['01', '03']
- Reason: Practitioner discussion of domain-specific sub-agent architecture (coordinator over specialist agents, 'tree of agents' pattern) and runtime diversity for agent execution, directly relevant to multi-agent orchestration design in the harness. The episode description and sampled excerpts consistently show harness-relevant content (agent coordination, runtimes, cost/ops concerns like unexpected bills from runaway agents), meeting the whole-episode judgement standard for podcasts.

## Noam Brown – Agent swarms, alignment, & recursive self-improvement
`podcast:93a1c773317f1e28`

- Before: defer []
- After: accept ['01', '02']
- Reason: Research-perspective interview with an OpenAI researcher discussing a specific multi-agent system claim (10,000 agents, 130B tokens, 88 hours) and reasoning about agent swarm coordination and alignment at scale, relevant to multi-agent orchestration design. The claim is a vendor/lab announcement without an independent method description, so it should be reported as OpenAI's claim rather than a verified measurement.

## Dyna-2: General Purpose Physical Agents with Hour-Long Autonomy — Jason Ma, Dyna Robotics
`podcast:ec31609f2b260a6c`

- Before: absent from first eligible corpus
- After: reject []
- Reason: This episode covers Dyna Robotics' world-action model for physical robot control (predicting future video/state to guide robot actions, deployments at restaurants/hotels) — it is about robotics model architecture and physical deployment, not about the software harness around LLM-based agents (context management, tool protocols, sandboxing, agent evals). The excerpts discuss dexterity, inference speed for physical tasks, and customer deployment stories with no mention of agent loops, MCP, permissions, or observability infrastructure relevant to this publication's scope. This is out of scope per the policy's focus on harness engineering for AI agents, not robotics/physical AI product content.

## Why Dwarkesh is Wrong about Computer Use + How OpenAI shipped its Jev competitor in 1 Week
`podcast:ef6c31b1a483418d`

- Before: accept ['01', '02']
- After: accept ['01', '03']
- Reason: This OpenAI DevDay interview with the computer-use product/engineering lead covers harness-relevant specifics: computer-use agent API additions, cost/speed tradeoffs of a new model specifically for computer use (claimed 5x-7x cost reduction vs prior model), the 'app shots' feature pulling full metadata/code context rather than a plain screenshot, and caching guarantees (30-minute default, a 12-hour preview window) relevant to production cost control. These are documented product behaviours and vendor claims about a computer-use harness, which is central to this publication's scope on tool interfaces and computer use. Vendor claims are presented as such and should be labeled as unverified cost multipliers absent independent measurement.

## The Agent Works. Does Anyone Trust It? — Michele Grant, Leading at Scale
`youtube:-a2oTS9J67U`

- Before: accept ['03']
- After: accept ['01', '03']
- Reason: This talk directly addresses harness-relevant operational concerns: a staged autonomy ladder for agent deployment (suggest/draft/approval/exceptions-only), the requirement for assigned decision ownership before expanding agent autonomy, and the specific risk that 'once humans only look at exceptions' oversight quality degrades — a concrete trust/permissions design pattern for production agents. It is a practitioner account (20+ years enterprise transformation experience) applying change-management discipline to agent rollout decisions, relevant to the permissions/approvals and production-operation scope of this publication.

## Code review is no longer the bottleneck
`youtube:IZXv6a78NDw`

- Before: defer []
- After: reject []
- Reason: This is a short promotional video for Codex's code-review feature (PR inbox, automated cloud review pass, private chat per PR) with no discussion of harness internals such as context handling, tool protocols, permissions, or evaluation methodology. It is marketing content demonstrating a UI workflow, which the policy excludes as marketing without technical content.

## Tokens Are the Cheap Part — Steve Jamison, Jellyfish
`youtube:U7ZYBCcdJPg`

- Before: accept ['01', '02']
- After: accept ['01', '02', '03']
- Reason: Jellyfish presents measured data (joined engineering-workflow and AI telemetry data) showing AI spend up 60x, merged PRs per engineer up 43%, a breakdown by spend quintile (top 20% of spend driving only incremental PR throughput gains, ~2.5B tokens/dev/month vs ~60M for lightest group), and revert-rate comparisons explicitly flagged as within noise — this is directly relevant to the publication's cost/production-operation scope and models good practice distinguishing measured signal from noise. It is a practitioner/research-style talk grounded in a described dataset and method, not a vendor feature pitch, meeting the policy's preference for measured results with a described comparison.

## What Technical Due Diligence Finds When the Deck Says “70% Automated” — Soukaïna Abelhad
`youtube:gDRCpTMCqEU`

- Before: accept ['02', '03']
- After: reject []
- Reason: This talk is about technical due diligence methodology for evaluating AI-automation claims in investment/M&A contexts (arithmetic checks on workload volume vs labor, judge validation questions) rather than harness engineering; it touches eval rigor only tangentially and is framed for investors/executives, not harness builders. It falls outside scope as general AI automation commentary with no harness design or protocol implication.

