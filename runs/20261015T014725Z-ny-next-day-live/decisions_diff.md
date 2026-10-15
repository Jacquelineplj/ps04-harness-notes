# New York next-day live run comparison

Previous complete run: `20261014T014037Z-second-live`. New complete run: `20261015T014725Z-ny-next-day-live`.

The earlier runs began on October 13 in America/New_York. This run began on October 14 at 21:47:25 EDT (October 15 at 01:47:25 UTC). See `execution_timezone.json` for machine-readable conversions. The as-of date remains the UTC execution date used by the pipeline.

Store observations: **20 new / 2 changed / 45 unchanged**. These changes are relative to the persistent store immediately before this run, rather than all differences from the originally published edition. The eligible corpus grew from 73 to 93; 3 records were excluded by the current 30-date window (September 16–October 15 UTC).

Selection: {'reject': 50, 'accept': 35, 'defer': 8}. The same policy v2 was used as in the previous complete run. Changes reflect the expanded corpus, a moving date window, and model variability; they are not a controlled policy experiment.

## New and changed observations

- **new** `feed:3e6e644f1b2b0e94` — Tree Appreciator; decision: reject; pieces: none.
- **new** `feed:154a39176d886b3b` — AI is mass decompiling games. That's both awesome and scary.; decision: reject; pieces: none.
- **changed** `feed:7e289d45dfc4cd8f` — Redesigning source control at Anthropic; decision: accept; pieces: 01, 03.
- **new** `feed:800e88b7ff797cb4` — Crossing the Threshold: How OpenAI and Anthropic Approach Autonomy and Safety in Financial Agents; decision: accept; pieces: 01, 03.
- **new** `feed:1d5f8df4a8f95858` — [AINews] AI Engineer NYC: Gemini 4 Argon, Vals AI Benchmarks; decision: reject; pieces: none.
- **new** `feed:504a28fcb44d1a3d` — HiRO-ACEv2: Simulating extreme weather at 3 km resolution for a fraction of the cost; decision: reject; pieces: none.
- **new** `feed:40c2e042484cc77c` — Euler: Towards Human-Centered Multi-Agent Mathematical Discovery; decision: reject; pieces: none.
- **new** `feed:abdcb8a376289470` — DeltaStreamer: Towards Human-Like Agentic Streaming Video Understanding; decision: defer; pieces: none.
- **new** `feed:265494f2f990955e` — LAGO: Language Agents with Reusable Growing Options; decision: accept; pieces: 01, 02.
- **new** `feed:9af0a9d6b90c27e2` — EGCForest: Structured Agent Memory Organization for Enterprise Group Chats; decision: accept; pieces: 01, 02.
- **new** `feed:90ab5356a1b22683` — Teaching Agents in their Own Style: Blackbox Teacher Distillation for Web Agents; decision: accept; pieces: 01, 02.
- **new** `feed:f6079d79e221ce0f` — ActionOPD: Distilling Decisions, Not Tokens; decision: defer; pieces: none.
- **new** `feed:d995256e997e50a5` — Build your slide template; decision: reject; pieces: none.
- **changed** `feed:231ac6df8b60f0a8` — Principles for effective slides; decision: reject; pieces: none.
- **new** `feed:b76b11a1199f73b7` — Google DeepMind and Singapore Government collaborate to build fine-tuned AI model for scam detection; decision: reject; pieces: none.
- **new** `youtube:0JZy5AuuQzc` — I Spent Two Years Building the Median — Hariprasad Sudharshan; decision: reject; pieces: none.
- **new** `youtube:tZycGA_Fbfo` — Paving the Road to Production: Governed Enterprise AI Agents — Harish Gaggar, Credit Karma; decision: accept; pieces: 01, 03.
- **new** `youtube:Wb2v9Phhnns` — Your AI Isn’t the Problem. Your Infrastructure Is. — Jiachen Jiang, Coder; decision: accept; pieces: 01, 03.
- **new** `youtube:8g1N_a3h9H0` — How to Actually Tokenmaxx and Save Millions — Alvin Pane, OutRival; decision: accept; pieces: 01, 02.
- **new** `youtube:7b9tov5Uc5s` — Rebuilding CI for AI-Scale Commit Volume — Gautam Korlam, SonarSource; decision: accept; pieces: 01, 03.
- **new** `youtube:hQSBJVreLms` — From Wet Lab to RL Env: 10,000 Drug-Discovery Campaigns in a Weekend — Ian Quigley, Leash Bio; decision: reject; pieces: none.
- **new** `podcast:4e22e3d6436deca5` — Uber’s AI infra, from the inside; decision: accept; pieces: 01, 03.

## Changed decisions and piece assignments

### AI is mass decompiling games. That's both awesome and scary.
`feed:154a39176d886b3b`

- Before: absent from previous eligible corpus 
- After: reject []
- Reason: This is a link-blog post about AI-powered game decompilation and preservation, which has no harness design, tool protocol, sandboxing, evaluation, or production-operation implication for agent builders. It falls under the excluded 'general AI commentary' and out-of-scope 'mentions agents only in passing' categories.

### [AINews] AI Engineer NYC: Gemini 4 Argon, Vals AI Benchmarks
`feed:1d5f8df4a8f95858`

- Before: absent from previous eligible corpus 
- After: reject []
- Reason: This is an AINews roundup/newsletter digest covering the Gemini 4 Argon GA launch and AI Engineer NYC conference; per policy, newsletter link roundups are secondary reporting and should be deferred/rejected when primary sources exist, and most content here (pricing, benchmark leaderboard confirmations, model launch news) lacks harness-design implications beyond passing mentions.

### LAGO: Language Agents with Reusable Growing Options
`feed:265494f2f990955e`

- Before: absent from previous eligible corpus 
- After: accept ['01', '02']
- Reason: Measured research on a multi-agent orchestration design: a meta-agent library of reusable 'options' tested on 500 SWE-bench Verified tasks, with a controlled 150-task comparison against mini-SWE-agent and Terminus 2 under matched policy/temperature/evaluator (60.3% vs 49.3%/57.3%) and an ablation isolating decomposition, reuse, and library contribution. This directly measures a harness design choice (sub-agent orchestration, option reuse) with method and comparison, squarely in scope.

### Tree Appreciator
`feed:3e6e644f1b2b0e94`

- Before: absent from previous eligible corpus 
- After: reject []
- Reason: A short personal anecdote about building a game with the Claude iPhone app; it touches on no harness design, tool protocol, sandboxing, evaluation, or production operation topic in scope, and at ~1000 characters is close to the policy's exclusion for short, thin posts without technical content.

### Euler: Towards Human-Centered Multi-Agent Mathematical Discovery
`feed:40c2e042484cc77c`

- Before: absent from previous eligible corpus 
- After: reject []
- Reason: Euler is a multi-agent framework for mathematical discovery addressing long-horizon context loss and verification, which touches harness concerns, but its focus is domain-specific (mathematical research workflows) rather than general harness design, and the brief excludes model-capability/domain-application papers without direct harness implication beyond a narrow case. The long-horizon context/memory problem it describes is generic but the paper's contribution is a math-specific representation, not a generalizable harness technique validated across domains.

### HiRO-ACEv2: Simulating extreme weather at 3 km resolution for a fraction of the cost
`feed:504a28fcb44d1a3d`

- Before: absent from previous eligible corpus 
- After: reject []
- Reason: This is a climate-emulation model (weather simulation) announcement with no connection to agent harness design, tool protocols, evaluation of agents, or production operation of agents; it is out of scope entirely under the topic definition.

### From Specialist Agents to Distributed Skills over MCP
`feed:6dfb9f1cb365f38e`

- Before: accept ['01', '02']
- After: accept ['01', '03']
- Reason: A detailed practitioner/commercial comparison of two multi-agent architectures (specialist agents via A2A vs. distributed skills/tools served over MCP), using the author's own ski-resort demo execution traces to examine differences in model calls, latency, and token consumption — directly on-topic for tool protocol design (MCP) and multi-agent orchestration. It offers concrete architectural tradeoffs and trace-based evidence rather than a bare announcement, serving piece 01 and 03 on orchestration design choices.

### Crossing the Threshold: How OpenAI and Anthropic Approach Autonomy and Safety in Financial Agents
`feed:800e88b7ff797cb4`

- Before: absent from previous eligible corpus 
- After: accept ['01', '03']
- Reason: Reports on conference keynotes from OpenAI and Two Sigma describing concrete permission/guardrail design choices for financial agents, including Two Sigma's specific controls to avoid 'approval fatigue' and OpenAI's framing of human-in-the-loop as a product design decision; this is directly in scope (permissions, approvals, guardrails in the harness) and offers practitioner detail beyond a model announcement. Evidence is vendor/practitioner conference commentary, not measured results, and should be labeled as such.

### Matched-Context Group Policy Optimization for LLM Agent Training
`feed:89a6239a0ab19877`

- Before: reject []
- After: accept ['02']
- Reason: Research paper measuring a credit-assignment technique (MCGPO) for training long-horizon LLM agents, with reported percentage-point improvements over a matched baseline (GraphGPO) across six environment-backbone settings and three seeds. This is exactly the kind of harness-relevant RL training measurement in scope (agent trajectory credit assignment), with a described method and quantified comparison. Novel development within the freshness window.

### Teaching Agents in their Own Style: Blackbox Teacher Distillation for Web Agents
`feed:90ab5356a1b22683`

- Before: absent from previous eligible corpus 
- After: accept ['01', '02']
- Reason: Research paper on distilling black-box teacher web agents into smaller open models via trajectory editing (WebKD), reporting 5.5-10.7pp gains over behavior cloning, outcome-RL, and teacher-editing baselines on named benchmarks (TimeWarp, OnlineMind2Web). Directly relevant to harness design for cost-efficient web agents, with described method and measured comparisons.

### EGCForest: Structured Agent Memory Organization for Enterprise Group Chats
`feed:9af0a9d6b90c27e2`

- Before: absent from previous eligible corpus 
- After: accept ['01', '02']
- Reason: Presents a concrete harness design for enterprise agent memory (EGCForest's channel/actor/artifact forests) with measured results on three enterprise-chat benchmarks, claiming up to 20.85-point accuracy improvement over MemOS. This is exactly the kind of memory-architecture research with described method and comparison that piece 02 can scrutinize and piece 01 can flag as a new development.

### DeltaStreamer: Towards Human-Like Agentic Streaming Video Understanding
`feed:abdcb8a376289470`

- Before: absent from previous eligible corpus 
- After: defer []
- Reason: Proposes an agentic streaming-video memory framework (change-aware memory plus query-driven replay) with benchmark results on OVO-Bench and StreamingBench, which touches context/memory management relevant to harness design, but the opening text does not clearly connect to the audience's typical agent-harness concerns (tool use, coding/computer-use agents) and needs further reading to judge whether it generalizes beyond a narrow video-understanding niche.

### Does being rude to AI work? What 6 models revealed
`feed:aed891eb1cf0d9a5`

- Before: reject []
- After: accept ['02']
- Reason: A practitioner-authored experiment testing whether rude vs. polite prompts change accuracy, token usage and behavior across six models, directly relevant to harness-level prompt/eval design, and it explicitly separates tone from brevity instructions to correct a conflated prior finding ('Mind Your Tone'). This is new measured analysis (own experiment plus critical comparison to two prior papers) that surfaces genuine tension in results across studies, fitting piece 02's mandate to report conflicting evidence.

### Google DeepMind and Singapore Government collaborate to build fine-tuned AI model for scam detection
`feed:b76b11a1199f73b7`

- Before: absent from previous eligible corpus 
- After: reject []
- Reason: This describes an on-device fine-tuned Gemma model for scam detection, a consumer safety product collaboration with no harness design, tool protocol, agent evaluation, or orchestration implication. It is an announcement of a government partnership, out of scope per the policy's exclusion of material that mentions AI only in passing relative to harness concerns.

### Build your slide template
`feed:d995256e997e50a5`

- Before: absent from previous eligible corpus 
- After: reject []
- Reason: This is a general guide to building slide templates (colour theory, typography, layout), with no connection to AI agent harness design, tool protocols, evaluation, or production operation; it falls under the policy's exclusion of generic how-to/tutorial content unrelated to the publication's scope.

### MC-EvoBench: Auditing Experience-Driven Self-Improvement in Minecraft Agents
`feed:e7a482afdd6942d5`

- Before: accept ['02', '03']
- After: defer []
- Reason: OPERATIONAL: no decision returned by the model for this item; deferred for human review, not an editorial judgement.

### Hello Python 3.15, goodbye 3.10, and now I can use 3.11
`feed:e8d8f43511a9291f`

- Before: reject []
- After: defer []
- Reason: OPERATIONAL: no decision returned by the model for this item; deferred for human review, not an editorial judgement.

### Foundry hosted agent isolation with Microsoft Agent Framework
`feed:eaac866ece437024`

- Before: accept ['01']
- After: defer []
- Reason: OPERATIONAL: no decision returned by the model for this item; deferred for human review, not an editorial judgement.

### Are Harnesses Worth the Cost?
`feed:ee6df3f002868714`

- Before: accept ['01', '02', '03']
- After: defer []
- Reason: OPERATIONAL: no decision returned by the model for this item; deferred for human review, not an editorial judgement.

### Returning to Development States: When Full Sandbox Snapshots Help Coding Agents
`feed:f52921adc97fb1dc`

- Before: accept ['01', '02']
- After: defer []
- Reason: OPERATIONAL: no decision returned by the model for this item; deferred for human review, not an editorial judgement.

### ActionOPD: Distilling Decisions, Not Tokens
`feed:f6079d79e221ce0f`

- Before: absent from previous eligible corpus 
- After: defer []
- Reason: OPERATIONAL: no decision returned by the model for this item; deferred for human review, not an editorial judgement.

### The model that didn't exist, so you made it yourself
`feed:ffd2818196374b7e`

- Before: reject []
- After: accept ['01', '03']
- Reason: A practitioner report describing a concrete agentic workflow (ML Intern) for distilling a 9B model into a 0.8B model, with specific numbers (99.7% valid output, quarter of teacher's tokens, $16 compute cost) and design details like budget enforcement, baseline requirements, and smoke tests before full runs -- directly relevant to harness permission/approval design and agent planning loops. It is a first-person account of deployed agent behavior, not a vendor announcement, giving it practitioner-report credibility.

### Uber’s AI infra, from the inside
`podcast:4e22e3d6436deca5`

- Before: absent from previous eligible corpus 
- After: accept ['01', '03']
- Reason: Detailed practitioner account from Uber's distinguished engineer of internal systems built around coding agents -- including MCP Gateway, AI Guard, permissions, and the explicit claim that 'the harness is the easy part, what's hard is all the things around them' -- directly addresses production operation, permissions, and MCP tooling at scale. This is a deployed-system practitioner report with named internal systems (Minion, Codeinbox, Shepard), giving concrete evidence beyond a vendor pitch.

### Noam Brown – Agent swarms, alignment, & recursive self-improvement
`podcast:93a1c773317f1e28`

- Before: accept ['01', '02']
- After: reject []
- Reason: The episode's lead mentions a 10,000-agent swarm using 130B tokens over 88 hours (a multi-agent orchestration scale claim), but the visible transcript focuses on reasoning-model scaling, alignment philosophy, and speculative 2030 automation timelines rather than harness design, tool protocols, evaluation methods, or production operation. The multi-agent swarm detail is asserted without method or harness specifics in the retained text, so it does not meet the bar for a harness-relevant claim.

### The Agent Works. Does Anyone Trust It? — Michele Grant, Leading at Scale
`youtube:-a2oTS9J67U`

- Before: accept ['01', '03']
- After: reject []
- Reason: This talk is about organizational trust-building and change management for enterprise AI rollouts (steering committees, value cases, autonomy stages tied to business sign-off), not harness engineering. It touches audit/exceptions review briefly but centers on business process and governance framing rather than any technical harness mechanism, which is out of scope per the policy's exclusion of general AI/business commentary without harness implication.

### I Spent Two Years Building the Median — Hariprasad Sudharshan
`youtube:0JZy5AuuQzc`

- Before: absent from previous eligible corpus 
- After: reject []
- Reason: This is a founder's personal narrative about building a product (a 'median' app) over two years, with one passing mention of harness terminology (tools, context, orchestration, memory, MCP) but no technical detail, measurement, or design analysis of harness choices. It reads as entrepreneurship/product-building commentary, which the policy excludes as general commentary without harness implication.

### Deploying AI Inside a Bank Is Not an Engineering Problem — Paden Gayle, Applied AI Engineers
`youtube:3ZlQk4-knWM`

- Before: accept ['01', '03']
- After: accept ['03']
- Reason: Describes a concrete autonomy-ladder design (suggest/draft/act-with-approval/act) and specific logging requirements (preserving input prompts, model version, config, output, reviewer action for reconstructing decisions) for deploying an agent in a regulated bank setting — this is documented practitioner design guidance on permissions/approvals and observability, squarely in the harness permissions/guardrails and production-operation scope. It is a practitioner report of applied design decisions rather than vendor marketing, useful for piece 03 on implications for regulated deployment.

### Rebuilding CI for AI-Scale Commit Volume — Gautam Korlam, SonarSource
`youtube:7b9tov5Uc5s`

- Before: absent from previous eligible corpus 
- After: accept ['01', '03']
- Reason: Describes concrete CI/build infrastructure bottlenecks caused by agent-scale commit volume (flaky tests, review becoming the dominant latency source per P90 measurement at Uber, need for compliance-recorded decisions on agent-authored code) drawing on the speaker's decade of build/merge infra experience at Uber and now Sonar. This is a practitioner report with a specific measurement claim (P90 review time dominance) relevant to production operation and reliability of agent-driven software delivery pipelines.

### How to Actually Tokenmaxx and Save Millions — Alvin Pane, OutRival
`youtube:8g1N_a3h9H0`

- Before: absent from previous eligible corpus 
- After: accept ['01', '02']
- Reason: Presents a specific evaluation methodology for prompt/model optimization at scale: an 'AA test' (ceiling test) to check whether production output is self-consistent before attributing changes to a prompt rewrite, plus statistical practice (confidence bounds crossing zero, per-category analysis) to validate whether a cheaper/optimized model is actually worse. This is a measured, method-described practitioner approach to agent evaluation and cost control, core to the eval/production-operation scope.

### Tokens Are the Cheap Part — Steve Jamison, Jellyfish
`youtube:U7ZYBCcdJPg`

- Before: accept ['01', '02', '03']
- After: accept ['01', '02']
- Reason: Jellyfish presents measured data from engineering workflow + AI telemetry across many organizations (AI spend up 60x YoY, merged PRs per engineer up 43%, cost-per-PR broken into spend quintiles, revert-rate comparison showing deltas within noise) to argue that token cost is a small fraction of true PR cost once human time is included — this is a harness-relevant cost/production-operation measurement with described method (quintile splits, revert rate proxy) directly useful to practitioners tracking agent cost and reliability.

### Your AI Isn’t the Problem. Your Infrastructure Is. — Jiachen Jiang, Coder
`youtube:Wb2v9Phhnns`

- Before: absent from previous eligible corpus 
- After: accept ['01', '03']
- Reason: A Coder staff PM walks through three real/anonymized incidents of coding-agent failures (e.g., an agent causing damage via the 'lethal trifecta' of tool access, with insufficient logging to catch it in real time) and derives concrete harness mitigations: short-lived scoped credentials, isolated/ephemeral workspaces, and better real-time logging — this is exactly the sandboxing/permissions/observability practitioner-report content the brief seeks, based on direct incident accounts rather than abstract advice.

### Managed Deep Agents | Deploying mission critical agents to production
`youtube:XcsspzECTKA`

- Before: accept ['01', '03']
- After: accept ['01']
- Reason: Describes documented product behavior for Managed Deep Agents: how the harness handles credential delegation ('whose account should it use'), connecting agents across surfaces, and runtime memory/connection management for production deployment. This is a vendor announcement with specific technical detail on permissions and identity delegation relevant to harness builders, though it is self-reported and should be labeled as vendor claim without independent measurement.

### What Technical Due Diligence Finds When the Deck Says “70% Automated” — Soukaïna Abelhad
`youtube:gDRCpTMCqEU`

- Before: reject []
- After: accept ['02', '03']
- Reason: Practitioner framework for scrutinizing automation claims in technical due diligence: proposes concrete checks (workload volume vs. fully-loaded human labor, judge validation methodology, cost-per-accepted-autonomous-task) grounded in a named controlled experiment (95 developers, JavaScript HTTP server task) and named public datasets (Faros). This directly serves the evaluation/measurement skepticism this publication is built around, distinguishing vendor-asserted automation percentages from what the underlying arithmetic supports.

### From Wet Lab to RL Env: 10,000 Drug-Discovery Campaigns in a Weekend — Ian Quigley, Leash Bio
`youtube:hQSBJVreLms`

- Before: absent from previous eligible corpus 
- After: reject []
- Reason: This is a long-form conversation about drug discovery, RL environments for chemistry, and molecule generation at Leash Bio—it concerns AI-for-science research, not harness engineering (context management, tool protocols, sandboxing, memory, agent evals, or orchestration). It is out of scope as general AI/domain-science content with no harness implication.

### Paving the Road to Production: Governed Enterprise AI Agents — Harish Gaggar, Credit Karma
`youtube:tZycGA_Fbfo`

- Before: absent from previous eligible corpus 
- After: accept ['01', '03']
- Reason: A Credit Karma senior staff engineer gives a practitioner report on moving agents to production, covering building internal MCP servers and gateways with security review of tools, LangGraph checkpointing per run/thread, a context optimizer that prunes payloads by token limit, memory, evals, and PII blocking before LLM calls. This is exactly the harness-engineering detail (MCP governance, context management, observability) the brief prioritizes, and the whole-episode rule applies since the sampled excerpts consistently show harness content.

### How to kill your SaaS: what we learned replacing a $43K/yr tool with AI agents
`youtube:zlD-CkLVKtU`

- Before: reject []
- After: accept ['01', '02']
- Reason: This describes a structured experiment running 56 AI-agent-built apps through automated business evals (40 with enough coverage to rank, top seven within 2.3 points of saturation) to replace a $43K/yr SaaS tool, offering measured comparison data and practitioner reflection on what 'vibe coding' actually requires (iterative building, not single-prompt generation). It is directly relevant to agent evaluation methodology and practitioner experience with coding agents, meeting the bar for measured-results-with-method evidence.


## Resulting editorial changes

The new briefs change the angles of the three pieces; these are new drafts and do not replace the previously approved published series.

- **Piece 01: The harness grew a second layer: what changed in agent infrastructure this month** — The month's developments cluster around a single shift: the hard problems have moved out of the agent loop and into the layer that surrounds it — tool retrieval and reliability, orchestration topology, credential and identity delegation, and the source-control and CI plumbing that agent-scale output overwhelms. Vendors announced new orchestration and deployment primitives (Anthropic's dynamic workflows, Microsoft's distributed skills over MCP, LangChain's Managed Deep Agents), while practitioners at Uber, Anthropic and Credit Karma described building essentially the same set of surrounding systems independently. The common finding across both camps is that the model and the loop are no longer the bottleneck.
- **Piece 02: Which numbers survive the method check: tool descriptions, scaffold comparisons, and what an eval actually measured** — The strongest results this month are the ones whose authors bounded their own claims — LAGO's controlled re-run of competing scaffolds, ThinkingBox's state-based grading, Arize's single-variable tool-description change. The weakest are not the vendor announcements but the widely-circulated numbers that conflated two variables at once, as Arize's own re-run of the prompt-tone experiments demonstrates. The recurring methodological lesson across research and practitioner work alike is that an agent eval that grades the trajectory or the final response, rather than the terminal state, systematically overstates success.
- **Piece 03: What to build next: identity, state-grading, and the cost line you are not measuring** — Three implications follow from the month's evidence that do not follow from any single item. First, the credential and identity layer is now the highest-leverage safety control in the harness, ahead of prompt-level guardrails, because every documented failure this month traced back to standing permissions rather than a model mistake. Second, teams should move their acceptance gate from trajectory inspection to terminal-state verification, and should budget for repeat runs rather than single passes. Third, the correct unit for agent cost control is not the token bill but the fully-loaded cost per accepted unit of work — a reframing that changes whether you cap spend or increase it.
