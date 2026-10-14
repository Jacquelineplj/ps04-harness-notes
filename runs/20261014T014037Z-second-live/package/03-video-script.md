# What To Change in Your Harness, and What To Watch

Runtime target: 4.9 minutes (approx. 732 narration words)

---

## 1. Hook

**Visual:** Dark slide, three stacked lines appearing one at a time: "trajectory → terminal state", "one run → repeat rate", "belief → model consistency". Harness Notes logo bottom-right.

**On-screen text:** Move the review effort, not the technique

**Narration:** This month, reconsider where you spend review effort: terminal state, repeated reliability, and feedback cadence matched to your model. Several sources also point to an organisational constraint: someone must own the agent's decisions.

---

## 2. Change one — grade the terminal state

**Visual:** Quote card. Publisher line: "Hugging Face — ThinkingBox authors, 3 October 2026." Four bullets beside it: check terminal state · classify errors · cut tool surface · gate irreversible changes.

**On-screen text:** Four changes. Zero measured lift.

**Narration:** The ThinkingBox authors, in a third of October Hugging Face post, give an unusually actionable list: check the terminal state before you commit instead of trusting the model's account of what it did, classify tool and system errors so retries target the recoverable ones, cut the tool surface to what the workflow actually needs, and require human approval on changes you cannot cheaply reverse. [1] The part worth respecting is the caveat they attach — they say plainly that they have not measured the lift from any of it. [1] That is a hypothesis list, not a results table.

---

## 3. Your eval matrix is probably too narrow

**Visual:** Simple timeline graphic: "Docs change passes eval matrix" → "Ships" → "Agents flag docs as injection" → "Rollback". Caption card: MLOps Community podcast, 28 September 2026.

**On-screen text:** "We didn't know our matrix wasn't big enough"

**Narration:** A related failure showed up on the MLOps Community podcast on the twenty-eighth of September, about twenty-seven minutes in. An AWS practitioner reports shipping an MCP documentation change that passed their eval matrix, then getting an email the next day because agents in production were flagging the Markdown docs as an attempted malicious injection. They rolled it back. [7] We read that as the strongest available argument that eval matrices for tool documentation are routinely too narrow — documentation is part of the harness surface you have to test.

---

## 4. Change two — cadence from the model

**Visual:** Two-column slide. Left: "Inconsistent unaided outcomes → continuous feedback during development." Right: "Passes in one shot → single final acceptance gate." Source strip: Thoughtworks, 13 October 2026.

**On-screen text:** Not whether sensors run. When.

**Narration:** Thoughtworks published Jain's harness-cost write-up on the thirteenth of October, and the conclusion is narrower than the title suggests. What changes with model capability is not whether independent sensors are needed, but when they run — continuous feedback during development for models whose unaided attempts are inconsistent, a single final acceptance gate for models that pass the brief in one shot. [2] If you are running a continuous harness against a model that already solves your tasks unaided, you are paying development overhead for a check you could do once at the end.

---

## 5. Change three — stop capping tokens

**Visual:** Bar chart described: one tall bar labelled "Engineer salary 97.5%", one sliver labelled "AI 2.5%". Below: "Cost per merged PR −26% over a year, at 83% of companies studied." Source strip: Steve Jamison, Jellyfish, AI Engineer, 13 October 2026.

**On-screen text:** AI is 2.5% of the cost per merged PR

**Narration:** Steve Jamison of Jellyfish, at AI Engineer on the thirteenth of October, reports that AI spend is roughly two and a half percent of the combined human-plus-AI intelligence cost of producing a merged pull request, and that cost per merged PR fell twenty-six percent over a year at eighty-three percent of the companies studied. [3] If that holds for your organisation, a tight token budget is more likely capping throughput gains than capping waste. Note the incentive: Jellyfish sells engineering analytics, and merged PRs are a throughput proxy the talk itself concedes may reflect larger PRs rather than more work.

---

## 6. The ownership constraint

**Visual:** Ladder graphic with four rungs: shadow · supervised draft · exception ensemble · exceptions-only. Red annotation on top rung: "vulnerability = what the agent failed to flag." Quote card: Michele Grant, AI Engineer, 13 October 2026.

**On-screen text:** A falling override rate may mean review slipped

**Narration:** Michele Grant, at AI Engineer on the thirteenth of October, around twelve minutes in, lays out a four-stage autonomy ladder — shadow, supervised draft, exception ensemble, exceptions-only — and warns that once humans review only exceptions, the biggest vulnerability becomes what the agent failed to flag, so a falling override rate may mean review depth has slipped rather than the agent improving. [4]

---

## 7. Provenance is the same object

**Visual:** Split card. Left: "Preserve: prompts · model version · config · output · reviewer action" — Paden Gayle, AI Engineer, 13 Oct 2026. Right: "Automatic logging · six months retention · human oversight · post-market monitoring" — Arize, 13 Oct 2026.

**On-screen text:** Your trace store is the system of record

**Narration:** Paden Gayle, from a bank deployment angle at the same event, argues the harness must preserve input prompts, model version, configuration, output and reviewer action — because calling the model again later may produce a different answer, which makes the preserved record, not the model, the system of record for a past decision. [5] Arize's EU AI Act guide, published the same day, reaches the same place from the regulatory direction, arguing high-risk obligations are engineering work: automatic logging, six months of retention under your control, human oversight, post-market monitoring on production traces. [6] Our interpretation is that the autonomy ladder and the provenance requirement are two views of one harness component — you cannot promote an agent up the ladder without the record that justifies the promotion, and that record has to be designed before the first trace. [8]

---

## 8. Limits and what to watch

**Visual:** Two-panel slide. Left panel "Weak here": illustrative M&A case · hypothetical bank workflow · vendor-authored guide · no team reported back. Right panel "Watch": Anthropic dynamic workflows (Latent Space, 12 Oct) · Microsoft skills-over-MCP (16 Sep).

**On-screen text:** Every recommendation here is a hypothesis

**Narration:** Be honest about the weakness. The ownership material is framework and experience, not measurement — an illustrative M&A case, a hypothetical bank workflow, and a vendor-authored compliance guide. We have no evidence this month from any team that tried these changes and reported back, so every recommendation here is a hypothesis sourced from someone else's context. What we think is worth watching: whether orchestration logic now moving into the model stays there. Anthropic's dynamic workflows, covered by Latent Space on the twelfth of October, and Microsoft's skills-over-MCP post from the sixteenth of September both frame the shift as removing developer-managed interconnections. [9] Whether that glue stays gone, or reappears as configuration you cannot inspect, is the question for the next edition. The full article and every source are linked in the description.

---

Description: This edition of Harness Notes covers three concrete changes to make in your agent harness now — grading terminal state, picking feedback cadence from your model, and rethinking token caps — plus the decision-ownership constraint that several independent sources converged on this month. Read the full article for the detail and caveats; all sources are linked below.

---
*Estimated runtime: 4.9 minutes at 150 words per minute. As of 2026-10-14. AI-assisted script from reviewed sources; the presenter may be an AI avatar.*

## Sources

- **[1]** (source claim) ThinkingBox's authors recommend checking terminal state before committing, classifying errors so retries target recoverable ones, cutting the tool surface, and requiring approval for irreversible changes — while stating they have not measured the lift from any of these.
  - huggingface, *The Agent Said It Was Done. The Database Disagreed.* (2026-10-03): [https://huggingface.co/blog/microsoft/thinkingbox](https://huggingface.co/blog/microsoft/thinkingbox) — "Classify tool and system errors so retries target the recoverable ones. Cut the tool surface to what the workflow needs. And require human approval on the changes you cannot cheaply reverse. We have not measured the lift from any of these on this benchmark"
- **[2]** (source claim) Jain's conclusion is that model capability changes when sensors run rather than whether they are needed: continuous feedback for models with inconsistent unaided outcomes, a single final acceptance gate for models that pass in one shot.
  - thoughtworks, *Are Harnesses Worth the Cost?* (2026-10-13): [https://martinfowler.com/articles/are-harnesses-worth-the-cost.html](https://martinfowler.com/articles/are-harnesses-worth-the-cost.html) — "What changes with model capability is not whether independent sensors are needed, but when they run."
- **[3]** (reported fact) Jellyfish reports that AI spend is about 2.5% of the combined human-plus-AI intelligence cost of producing a merged PR, and that cost per merged PR fell 26% over a year at 83% of the companies studied.
  - ai-engineer, *Tokens Are the Cheap Part — Steve Jamison, Jellyfish* (2026-10-13), at 3:33: [https://www.youtube.com/watch?v=U7ZYBCcdJPg&t=212s](https://www.youtube.com/watch?v=U7ZYBCcdJPg&t=212s) — "What you pay your engineers plus what you pay for AI. Put them together in one cost bucket. AI is about 2 and 1/2% of the cost to produce another unit of merged code. Salary is the other 97 and 1/2%. This is in line with other reported figures, and this data is from August 2026."
  - ai-engineer, *Tokens Are the Cheap Part — Steve Jamison, Jellyfish* (2026-10-13), at 4:25: [https://www.youtube.com/watch?v=U7ZYBCcdJPg&t=264s](https://www.youtube.com/watch?v=U7ZYBCcdJPg&t=264s) — "time is factored in, and some level of quality gates has been cleared. What That decline in cost per merged PR includes a 60x increase in AI costs over the same time frame. The change is nearly universal, too. 83% of the companies we studied showed a drop in cost per PR. What does this tell us? The additional throug..."
- **[4]** (source claim) Michele Grant argues for a four-stage autonomy ladder and warns that once humans review only exceptions, the biggest vulnerability becomes what the agent failed to flag, so a falling override rate may mean review depth has slipped rather than the agent improving.
  - ai-engineer, *The Agent Works. Does Anyone Trust It? — Michele Grant, Leading at Scale* (2026-10-13), at 12:36: [https://www.youtube.com/watch?v=-a2oTS9J67U&t=755s](https://www.youtube.com/watch?v=-a2oTS9J67U&t=755s) — "the claims. Then we have stage four, where it's exceptions only. The analyst reviews only high-risk anomalies supported by periodic independent sampling. Pay close attention to stage four, however, because once humans only look at exceptions, your biggest vulnerability"
  - ai-engineer, *The Agent Works. Does Anyone Trust It? — Michele Grant, Leading at Scale* (2026-10-13), at 12:59: [https://www.youtube.com/watch?v=-a2oTS9J67U&t=778s](https://www.youtube.com/watch?v=-a2oTS9J67U&t=778s) — "is what the agent failed to flag. So I advise tracking mis material issues through independent sampling, monitoring error severity and watching your override rate carefully. A falling override rate does not automatically mean the agent is getting smarter. It can also mean the depth of review has slipped."
- **[5]** (source claim) Paden Gayle argues the harness must preserve input prompts, model version, configuration, output and reviewer action because re-calling the model later may produce a different answer, making the preserved record — not the model — the system of record for a past decision.
  - ai-engineer, *Deploying AI Inside a Bank Is Not an Engineering Problem — Paden Gayle, Applied AI Engineers* (2026-10-13), at 12:24: [https://www.youtube.com/watch?v=3ZlQk4-knWM&t=743s](https://www.youtube.com/watch?v=3ZlQk4-knWM&t=743s) — "five files make the review complete. Intended use, record users, boundaries and prohibited actions. Data lineage, records, each example source and use approval, failure modes, records detection and fallback, results by segment, record coverage and errors controls, record reviews, thresholds, stopping rules and owner..."
- **[6]** (source claim) Arize's compliance guide argues that EU AI Act high-risk obligations translate into harness engineering work — automatic logging, six months of retention under your control, human oversight, and post-market monitoring on production traces.
  - arize, *EU AI Act compliance for AI agents: a practical engineering guide* (2026-10-13): [https://arize.com/blog/eu-ai-act-compliance-ai-agents](https://arize.com/blog/eu-ai-act-compliance-ai-agents) — "Most high-risk obligations are engineering work. Automatic logs, six months of retention, human oversight, post-market monitoring, incident handling, and explanations of decisions are things you build."
- **[7]** (reported fact) An AWS practitioner reports that an MCP documentation change passed their eval matrix but triggered agents in production to flag the Markdown docs as attempting a malicious injection, forcing a rollback — evidence that eval matrices for tool documentation are routinely too narrow.
  - mlops-community, *AWS Has 16,000 APIs. Can MCP Handle It?* (2026-09-28), at 27:29: [https://podcasters.spotify.com/pod/show/mlops/episodes/AWS-Has-16-000-APIs--Can-MCP-Handle-It-e3pgb4a](https://podcasters.spotify.com/pod/show/mlops/episodes/AWS-Has-16-000-APIs--Can-MCP-Handle-It-e3pgb4a) — "and it was very carefully created to not trigger all the things. We rolled it out and then the next day I get an email that is like, hey, my agent is telling me that the Markdown docs on AWS are trying to do an injection of something potentially malicious. I'm like, rollback, rollback. We didn't know our matrix wasn..."
- **[8]** (our inference) The autonomy ladder and the decision-provenance requirement are two views of one harness component: you cannot promote an agent up the ladder without the preserved record that justifies the promotion, and the record must be designed before the first trace.
  - ai-engineer, *The Agent Works. Does Anyone Trust It? — Michele Grant, Leading at Scale* (2026-10-13), at 9:54: [https://www.youtube.com/watch?v=-a2oTS9J67U&t=594s](https://www.youtube.com/watch?v=-a2oTS9J67U&t=594s) — "The evidence for greater autonomy comes from how the agent is built. I look for three artifacts. The first is an auditable decision log. For every workstream the agent evaluates, it records the raw data ingested, the tool calls executed, the prompt, and the mono versions. Output generated along with the human"
  - ai-engineer, *Deploying AI Inside a Bank Is Not an Engineering Problem — Paden Gayle, Applied AI Engineers* (2026-10-13), at 1:43: [https://www.youtube.com/watch?v=3ZlQk4-knWM&t=102s](https://www.youtube.com/watch?v=3ZlQk4-knWM&t=102s) — "looked like. Learn who will own the system after launch and what evidence that owner will need to maintain it. For third party risk, draw the actual dependency chain. Include the model provider, the host arrangements, and your role in the operating service. Find out which relationships have already been reviewed and..."
  - arize, *EU AI Act compliance for AI agents: a practical engineering guide* (2026-10-13): [https://arize.com/blog/eu-ai-act-compliance-ai-agents](https://arize.com/blog/eu-ai-act-compliance-ai-agents) — "Logs only count as evidence if you can prove what they say. Integrity, completeness, retention, and privacy have to be designed in from the first trace."
- **[9]** (our inference) What to watch next: whether orchestration logic now moving into the model (Anthropic's flows, Microsoft's skills-in-the-orchestrator pattern) stays there, since both vendors frame it as removing developer-managed interconnections.
  - latent-space, *How Anthropic’s Dynamic Workflows Coordinate Claude Agents* (2026-10-12): [https://latent.space/p/claude-dynamic-workflows](https://latent.space/p/claude-dynamic-workflows) — "it’s able to accomplish discrete, verifiable units of work without you having to manage any of the interconnections between these things"
  - microsoft, *From Specialist Agents to Distributed Skills over MCP* (2026-09-16): [https://devblogs.microsoft.com/agent-framework/from-specialist-agents-to-distributed-skills-over-mcp](https://devblogs.microsoft.com/agent-framework/from-specialist-agents-to-distributed-skills-over-mcp) — "The useful distinction is not “many services versus one service” or even “A2A versus MCP.” It is delegating a task to another reasoner versus giving the current reasoner a competence and access to its operations."
