# The Harness Moved Up a Layer: What Changed in Agent Infrastructure This Month

Runtime target: approximately 4 minutes 15 seconds (about 610 narration words)

## 1. Hook

**Visual:** Title card on dark background. Below it, four short bullets fade in one at a time: "tool retrieval," "orchestration," "state recovery," "verification." Optional avatar presenter in lower third.

**On-screen text:** The harness absorbed four jobs this month

**Narration:** This month, the agent harness quietly took over work that used to belong to the model or to the human operator — choosing tools by how reliably they actually execute, writing its own orchestration program, and grading itself on backend state instead of tool calls. Most of what you'll read about this is announcements. Two items carry real measurements, and we think those two are the ones worth your afternoon.

## 2. The one controlled experiment

**Visual:** Simple bar chart described on slide: two pairs of bars. "Luna, no harness: 3 of 10." "Luna, with harness: 10 of 10." "Sol, no harness: 10 of 10." "Sol, with harness: 10 of 10." Source line: martinfowler.com, Naresh Jain, 13 October 2026.

**On-screen text:** Luna: 3 of 10 → 10 of 10. Sol: unchanged.

**Narration:** Naresh Jain's piece on martinfowler.com is the cleanest result of the month, because it holds the task fixed and varies only the harness. Running the same API service build ten times per condition, he reports a cost-optimized model, GPT-6 Luna, going from three of ten accepted runs to ten out of ten with a behavioral harness — while the frontier model, GPT-6 Sol, passed all ten either way. [1]

## 3. Why the asymmetry is the finding

**Visual:** Quote card: "A harness that does nothing for your strongest model may be the difference between unusable and dependable for a cheaper one." Attributed on screen as Harness Notes interpretation.

**On-screen text:** Test the model you ship, not your best one

**Narration:** We read the asymmetry as the actual finding. There is no model-independent answer to "does the harness help." And if you're evaluating harness investment against a frontier model only, your experiment may be structurally incapable of detecting the benefit. [1]

## 4. Graders looking at the wrong thing

**Visual:** Quote card: "Of 79,853 failed attempts, 67.24% still terminated cleanly, invoked a state-changing tool, and reported no final tool error." Publisher line: ThinkingBox, Hugging Face, 3 October 2026.

**On-screen text:** 67.24% of failures looked clean

**Narration:** The second measured item is ThinkingBox, published on Hugging Face, which grades agents on terminal database state instead of on trajectories. Across twelve models, the authors report seventy-nine thousand eight hundred and fifty-three failed attempts — of which sixty-seven point two four percent nonetheless terminated cleanly, invoked a state-changing tool, and reported no final tool error. [2] A tool-call-based grader would have scored two thirds of real failures as fine.

## 5. The same blind spot at small scale

**Visual:** Side-by-side slide: left column "Score: PASS (all five configs)." Right column "Trace: 51 unnecessary skill loads, $11.85." Arrow to "1 tool description changed → 0 loads, $8.34." Source line: Arize, 12 October 2026.

**On-screen text:** $11.85 → $8.34, correctness unchanged

**Narration:** Arize's Harbor and Phoenix walkthrough hits the same blind spot from the opposite end — small scale, production tooling. Arize reports that every configuration passed the correctness benchmark, but inspecting traces revealed Codex loading an unnecessary skill repeatedly. Changing one tool description cut those loads from fifty-one to zero, and the run cost from eleven dollars eighty-five to eight thirty-four, correctness unchanged. [3] The score was never going to find that. The trace did.

## 6. Retrieval that knows what's broken

**Visual:** Slide with two stacked numbers: "Fault selection rate: 86.2% → 2.9%" and "Added latency: under 1 ms." Caveat band across the bottom: "Simulated 30% API failure rate." Source: RATED, arXiv, 9 October 2026.

**On-screen text:** 86.2% → 2.9%, under 1 ms

**Narration:** The RATED paper applies the same logic one layer down. Tool retrieval has historically ranked on semantic relevance; RATED adds a contextual bandit that re-ranks on live execution feedback. The authors report that under a simulated thirty percent API failure rate, fault selection rate dropped from eighty-six point two percent to two point nine percent, with under a millisecond of added latency. [4] If that holds outside simulation, it's cheap enough to be uncontroversial.

## 7. The vendor side, labelled as such

**Visual:** Two stacked quote cards. Top: "Claude itself determines how to divide and orchestrate the work" — Latent Space, 12 October 2026. Bottom: "the core harness has to be actually quite complex and very secure" — Thariq Shihipar, Latent Space podcast, 29 September 2026, at 46:22.

**On-screen text:** Claims, not measurements

**Narration:** On the vendor side, Latent Space reports that Anthropic's new dynamic workflows lets Claude write its own orchestration program, replacing the earlier requirement that developers configure a coordinator and a roster of subagents. [5] That's a claim about a product surface — nobody outside Anthropic has published numbers. And on the Latent Space podcast, about forty-six minutes in, Anthropic's Thariq Shihipar said the core Claude Code harness has to be quite complex and very secure — sandbox, permission approvals, computer use, MCPs, web access — even as the interaction layer above it changes freely. [7]

## 8. The through-line

**Visual:** Three-row slide. "RATED: stops trusting relevance, watches execution." "ThinkingBox: stops trusting tool calls, watches state." "Arize: stops trusting the score, watches the trace."

**On-screen text:** Stop deciding on proxies

**Narration:** Our interpretation: these are all the same move. Each one replaces a proxy signal in the harness with an observation of what actually executed. [8] The recurring failure is a harness deciding on a proxy that doesn't carry the information the decision needs.

## 9. Takeaway and limits

**Visual:** Split slide. Left: "Do now" — test against your shipping model; add a state-level check; keep traces next to scores. Right: "Thin evidence" — one greenfield Java service; simulated failures; no legacy-codebase measurement. End card pointing to the article.

**On-screen text:** Act on three. Treat the rest as claims.

**Narration:** So: test harnesses against the model you actually ship [1], assume a tool-call grader is blind to a large share of real failures [2], and keep traces next to scores — the cheapest win this month came from reading tool counts, not pass rates. [3] Honestly, the measured evidence is thin. Jain's study is one greenfield Java service at low reasoning effort [1], RATED's gains come from injected failures in simulation [4], and nothing this month measures harness effects on legacy codebases, which is where most of us actually work. The full article and every source are linked below.

Description: A four-minute evidence-first read on what actually changed in agent harness design this month — including a controlled experiment where a behavioral harness took a cost-optimized model from 3 of 10 runs to 10 of 10, and a benchmark finding that 67% of real agent failures look clean to a tool-call grader. Full article and every source cited are linked below.

---
*Estimated runtime: 4.1 minutes at 150 words per minute. As of 2026-10-14. AI-assisted script from reviewed sources; the presenter may be an AI avatar.*

## Sources

- **[1]** (reported fact) In a controlled 10-run comparison, a behavioral harness took GPT-6 Luna from 3 of 10 accepted runs to 10 of 10, while GPT-6 Sol passed all 10 runs with or without the harness.
  - thoughtworks, *Are Harnesses Worth the Cost?* (2026-10-13): [https://martinfowler.com/articles/are-harnesses-worth-the-cost.html](https://martinfowler.com/articles/are-harnesses-worth-the-cost.html) — "A frontier model, GPT-6 Sol, passed every external evaluation either way. But a cost-optimized model, GPT-6 Luna, succeeded in only 3 of 10 unharnessed runs and all 10 with the harness."
- **[2]** (reported fact) ThinkingBox reports that of 79,853 failed attempts across 12 models, 67.24% still terminated cleanly, invoked a state-changing tool, and reported no final tool error — meaning a tool-call-based grader would have missed them.
  - huggingface, *The Agent Said It Was Done. The Database Disagreed.* (2026-10-03): [https://huggingface.co/blog/microsoft/thinkingbox](https://huggingface.co/blog/microsoft/thinkingbox) — "In a common-set ablation covering 121,680 valid trials across 12 LLM models, 79,853 attempts failed the executable checks. Of those failures, 67.24% still terminated cleanly, invoked a state-changing tool, and reported no final tool error."
- **[3]** (reported fact) Arize reports that changing one tool description reduced Codex's unnecessary skill loads from 51 to zero and cut the benchmark run cost from $11.85 to $8.34 with correctness unchanged, a problem found by inspecting traces rather than scores.
  - arize, *How to test agent tool descriptions with Harbor and Phoenix* (2026-10-12): [https://arize.com/blog/how-to-test-agent-tool-descriptions-with-harbor-and-phoenix](https://arize.com/blog/how-to-test-agent-tool-descriptions-with-harbor-and-phoenix) — "Changing one tool description reduced Codex’s unnecessary skill loads from 51 to zero and lowered the cost of our benchmark run from $11.85 to $8.34. Correctness stayed unchanged on the benchmark."
- **[4]** (reported fact) The RATED paper reports that incorporating execution feedback via a contextual bandit cut fault selection rate from 86.2% to 2.9% under a 30% simulated API failure rate, with under 1 ms added latency.
  - arxiv, *RATED: Reliability-Aware AI Agent Tool Retrieval via Execution Dynamics* (2026-10-09): [https://arxiv.org/abs/2610.13889](https://arxiv.org/abs/2610.13889) — "reduces fault selection rate from 86.2% to 2.9% under severe API outage scenarios with a 30% failure rate, while incurring negligible latency overhead of less than 1 ms over encode-only inference"
- **[5]** (source claim) Latent Space reports that Anthropic's new 'dynamic workflows' feature lets Claude write its own orchestration program, replacing the previous requirement that developers configure a coordinator and a roster of subagents.
  - latent-space, *How Anthropic’s Dynamic Workflows Coordinate Claude Agents* (2026-10-12): [https://latent.space/p/claude-dynamic-workflows](https://latent.space/p/claude-dynamic-workflows) — "Previously, Claude Managed Agents required developers to configure a coordinator and a roster of subagents. With dynamic workflows, Claude itself determines how to divide and orchestrate the work."
- **[6]** (source claim) Simon Willison reports, citing Anthropic's own engineering writeup, that Anthropic's merged code changes rose from roughly 2,500 per day in May 2026 to over 30,000 per day in September, prompting a custom source-control system built for roughly 25 million checkouts per day.
  - simon-willison, *Redesigning source control at Anthropic* (2026-10-13): [https://simonwillison.net/2026/Oct/13/redesigning-source-control-at-anthropic](https://simonwillison.net/2026/Oct/13/redesigning-source-control-at-anthropic) — "In May 2026, Anthropic averaged around 2,500 code changes merged per day; as of September, we merged over 30,000 per day."
  - simon-willison, *Redesigning source control at Anthropic* (2026-10-13): [https://simonwillison.net/2026/Oct/13/redesigning-source-control-at-anthropic](https://simonwillison.net/2026/Oct/13/redesigning-source-control-at-anthropic) — "We perform on the order of 25 million code checkouts per day for CI, before counting developer environments, agent sandboxes, and research jobs."
- **[7]** (source claim) Anthropic's Thariq Shihipar describes the core Claude Code harness as necessarily complex and security-sensitive — requiring a sandbox, permission approvals, computer use, MCPs and web access — even as the interaction layer around it changes.
  - latent-space, *Claude Code’s Next Era — Thariq Shihipar, Anthropic* (2026-09-29), at 46:22: [https://latent.space/p/thariq](https://latent.space/p/thariq) — "yeah, approvals, it needs computer use and MCPs and all of these ways of accessing your data and it needs web search and web fadge. So as the models can do more and more, the core harness has to be actually quite complex and very secure, but then how you interact with it can change quite a lot. What other harness en..."
- **[8]** (our inference) The month's developments across research, vendor products, and practitioner reports converge on a single design move: replacing proxy signals in the harness (semantic relevance, well-formed tool calls, green rewards) with observations of actual execution outcomes.
  - arxiv, *RATED: Reliability-Aware AI Agent Tool Retrieval via Execution Dynamics* (2026-10-09): [https://arxiv.org/abs/2610.13889](https://arxiv.org/abs/2610.13889) — "Existing methods optimize semantic relevance but largely ignore tool availability during execution."
  - huggingface, *The Agent Said It Was Done. The Database Disagreed.* (2026-10-03): [https://huggingface.co/blog/microsoft/thinkingbox](https://huggingface.co/blog/microsoft/thinkingbox) — "A tool call is not an outcome Final responses and valid tool calls are only proxies. An agent can sound correct while leaving the wrong value, changing the wrong record, or creating an extra side effect."
  - arize, *How to test agent tool descriptions with Harbor and Phoenix* (2026-10-12): [https://arize.com/blog/how-to-test-agent-tool-descriptions-with-harbor-and-phoenix](https://arize.com/blog/how-to-test-agent-tool-descriptions-with-harbor-and-phoenix) — "Keep the trace next to the score. The score said pass every time. The tool count and the cost said something was off."
