# Which Harness Claims Survive Contact With Method

Runtime target: about 4 minutes 15 seconds (roughly 615 narration words)

---

## 1. Hook

**Visual:** Title card, dark background. Two columns forming: left "Described method, matched budget, stated uncertainty", right "Assertions in the costume of results". Optional avatar presenter in corner.

**On-screen text:** Sorted by evidence, the month splits cleanly

**Narration:** If you sort this month's agent-harness news by evidence quality instead of by headline, it splits cleanly in two. A handful of claims arrive with a described method, a matched budget, and honest uncertainty. A much larger set are vendor assertions or structural observations wearing the costume of results. And the real tensions this month are not vendor versus skeptic — they're between findings that differ because the tasks differ. We think the most instructive sources are the ones that report a negative result and then name the condition that carried it.

---

## 2. The best-evidenced claim refutes its own authors

**Visual:** Quote card styled as a paper header — "Returning to Development States: When Full Sandbox Snapshots Help Coding Agents", arXiv, 9 October 2026. Beneath it, a simple bar pair: Retry 17/25, Snapshot branching 6/25.

**On-screen text:** Retry 17/25. Snapshot branching 6/25.

**Narration:** The clearest piece of method came from a 9 October arXiv preprint on sandbox snapshots for coding agents, co-authored from Daytona. The authors stated a hypothesis — that branching from promising snapshots should beat plain independent retry under a fixed token budget — and then reported that it failed. Under a matched one-million-token budget, on a pre-registered harder Terminal-Bench subset, independent retry solved seventeen of twenty-five task-seed pairs while snapshot branching solved six [1].

---

## 3. The boundary condition

**Visual:** Same paper card, second slide. Icon of a SQLite database sitting outside a git folder. Numbers: full snapshot 4/5, source-only restoration 0/5.

**On-screen text:** State outside git: snapshot 4/5, source-only 0/5

**Narration:** What makes the paper useful is that it doesn't stop at the refutation. It isolates the condition under which full snapshots do win. On a custom task whose progress lived in a SQLite database outside git, full snapshot restore solved four of five attempts while source-only restoration solved zero of five [2]. That's the shape of a conditional result: hypothesis, matched budget, refutation, boundary.

---

## 4. Rigs that can't see what they measure

**Visual:** Quote card — Hugging Face post, "The Agent Said It Was Done. The Database Disagreed.", 3 October 2026. Two bars at different heights labelled pass@1, and two identical bars labelled "all 20 attempts: 241".

**On-screen text:** Headline gain. Same 241 tasks.

**Narration:** A 3 October Hugging Face post on the ThinkingBox benchmark makes a point that's easy to miss on a leaderboard. It reports that Claude Opus 5.5 scored higher than Claude Opus 5 on the single-attempt average, yet passed exactly the same number of tasks on all twenty attempts — two hundred forty-one — so the headline gain bought no additional dependability [3]. We read that as a statement about measurement, not about model quality.

---

## 5. Discipline, where you find it

**Visual:** B-roll of a conference stage, then a quote card: Steve Jamison, Jellyfish, AI Engineer, 13 October 2026, "slightly below the noise in the data".

**On-screen text:** "Not evidence of an improvement"

**Narration:** The same discipline shows up at the AI Engineer event on 13 October. Steve Jamison of Jellyfish, about ten minutes into his cost-per-pull-request talk, discusses revert rates as a quality proxy — and explicitly marks the deltas as slightly below the noise in the data, saying it is not evidence of an improvement [7]. That's a small act of restraint, and it's rarer than it should be.

---

## 6. Vendor claims, labelled and unlabelled

**Visual:** Quote card — Microsoft, "From Specialist Agents to Distributed Skills over MCP", 16 September 2026. Callout: "+22% tokens, fewer model calls, three runs".

**On-screen text:** "Not a controlled performance or quality study"

**Narration:** Microsoft's 16 September post on distributed skills over MCP is unusually careful for a vendor piece. It reports the skills path used about twenty-two percent more tokens across three runs despite fewer model calls, and the authors themselves label the comparison as not a controlled performance or quality study [4]. The honesty is real. It is still three runs, and three runs don't establish an architectural property.

---

## 7. Unverified by construction

**Visual:** Split card. Left: X-AgentRed, arXiv, 9 October 2026 — "1.77x harmful path rate, 2.99x tool coverage, one run per configuration". Right: Dwarkesh Podcast, 17 September 2026, Noam Brown.

**On-screen text:** Real numbers. Unavailable causal claims.

**Narration:** Two items stay unverified by construction. The X-AgentRed red-teaming preprint reports one-point-seven-seven times the harmful path rate and nearly three times the tool coverage of its baseline across four frontier agents — but states each configuration was evaluated in a single run inside a fixed simulated ecosystem [5]. And on the Dwarkesh podcast, about five minutes in, OpenAI's Noam Brown says of the reported ten-thousand-agent run that the experiments are simply too expensive to ablate at that scale [6]. The number is real; the causal claim isn't available.

---

## 8. The conflicts dissolve into task dependence

**Visual:** Two arrows converging on one box labelled "Task dependence". Left arrow: Thoughtworks, 13 October 2026. Right arrow: snapshot paper.

**On-screen text:** Not a disagreement. One conditional, twice.

**Narration:** So where's the conflict? We think there isn't one. Thoughtworks' 13 October harness writeup reports its own refuted expectation: a behavioural harness is not an automatic win for every model on every task. The snapshot paper lands in the same place from the other side — fresh retries suffice for file-centric work, and snapshots only become compelling when progress escapes the repository [8]. Reading these as a disagreement is a mistake.

---

## 9. Takeaway and limits

**Visual:** Closing slide: "Ask under which condition." Three bullets: check if state escapes the repo; check if unaided attempts are already consistent; report all-attempts alongside pass@1. Footer: limitations line.

**On-screen text:** Ask "under which condition", not "does it help"

**Narration:** The practical move is to stop asking whether snapshots or scaffolding help, and start asking under which condition — and to report the all-attempts column next to pass at one. Honestly, though: several of these are preprints with no independent replication, the snapshot paper evaluates its own co-author's sandbox product, and we found no source this month contradicting the task-dependence reading — which is an absence, not support. The full article and every source are linked in the description.

---

Description: This month's agent-harness claims, sorted by evidence quality — a refuted snapshot hypothesis, a benchmark gain that bought no dependability, and two results that only look like a disagreement. Full write-up in the linked article, with every source linked below.

---
*Estimated runtime: 4.4 minutes at 150 words per minute. As of 2026-10-14. AI-assisted script from reviewed sources; the presenter may be an AI avatar.*

## Sources

- **[1]** (reported fact) Under a matched one-million-token budget on a pre-registered Terminal-Bench subset, independent retry solved 17 of 25 task-seed pairs while snapshot branching solved 6 of 25, refuting the authors' own hypothesis.
  - arxiv, *Returning to Development States: When Full Sandbox Snapshots Help Coding Agents* (2026-10-09): [https://arxiv.org/abs/2610.13841](https://arxiv.org/abs/2610.13841) — "harder Terminal-Bench subset, retry solves 17/25 tasks while snapshot-based search solves 6/25, establishing that reliable restoration alone is not suffi- cient to improve test-time scaling (Section 5). •"
- **[2]** (reported fact) The same paper isolates the condition under which full snapshots do win: on a task whose progress lived in a SQLite database outside git, full snapshot restore solved 4 of 5 seeds while clean restart and git-diff restoration each solved 0 of 5.
  - arxiv, *Returning to Development States: When Full Sandbox Snapshots Help Coding Agents* (2026-10-09): [https://arxiv.org/abs/2610.13841](https://arxiv.org/abs/2610.13841) — "On extract-elf, compressed source-level state can outperform a full snapshot, while on a custom task whose progress lives in a SQLite database outside git, full snapshots solve 4/5 attempts and source-only restoration solves 0/5"
- **[3]** (reported fact) ThinkingBox reports that Claude Opus 5.5 scored higher than Claude Opus 5 on single-attempt average yet passed exactly the same number of tasks on all 20 attempts (241), so the headline gain bought no additional dependability.
  - huggingface, *The Agent Said It Was Done. The Database Disagreed.* (2026-10-03): [https://huggingface.co/blog/microsoft/thinkingbox](https://huggingface.co/blog/microsoft/thinkingbox) — "It passes exactly the same number of tasks on all 20 attempts: 241. Half a point of headline accuracy bought no additional dependability at all."
- **[4]** (reported fact) Microsoft's own comparison of distributed skills versus specialist agents reports the skills path used about 22% more tokens across three runs despite fewer model calls, and the authors label the comparison as not a controlled study.
  - microsoft, *From Specialist Agents to Distributed Skills over MCP* (2026-09-16): [https://devblogs.microsoft.com/agent-framework/from-specialist-agents-to-distributed-skills-over-mcp](https://devblogs.microsoft.com/agent-framework/from-specialist-agents-to-distributed-skills-over-mcp) — "Across three runs, native skills consumed 13,533 observed tokens versus 11,134 for A2A, about 22% more. Fewer model calls did not mean less cumulative context."
  - microsoft, *From Specialist Agents to Distributed Skills over MCP* (2026-09-16): [https://devblogs.microsoft.com/agent-framework/from-specialist-agents-to-distributed-skills-over-mcp](https://devblogs.microsoft.com/agent-framework/from-specialist-agents-to-distributed-skills-over-mcp) — "This is a three-pair illustration, not a controlled performance or quality study. Processes were reused, prompt-cache hits varied, and live telemetry changed during cooldowns."
- **[5]** (reported fact) X-AgentRed reports 1.77x the harmful path rate and 2.99x the tool coverage of STAC across four frontier agents, but each configuration was evaluated in a single run within a fixed simulated ecosystem.
  - arxiv, *X-AgentRed: Red-Teaming Personal Agents in Evolving Multi-Service Ecosystems* (2026-10-09): [https://arxiv.org/abs/2610.13886](https://arxiv.org/abs/2610.13886) — "Across four frontier agentic models, X-AgentRed achieves \(1.77\times\) the harmful path rate of STAC and explores a more diverse set of tools, yielding \(2.99\times\) the tool coverage on average."
  - arxiv, *X-AgentRed: Red-Teaming Personal Agents in Evolving Multi-Service Ecosystems* (2026-10-09): [https://arxiv.org/abs/2610.13886](https://arxiv.org/abs/2610.13886) — "Each configuration is evaluated in one run within a fixed simulated ecosystem."
- **[6]** (source claim) OpenAI's Noam Brown, discussing the reported 10,000-agent Navier-Stokes run, says the science on multi-agent scaling at that size does not exist and that the experiments are too expensive to ablate.
  - dwarkesh, *Noam Brown – Agent swarms, alignment, & recursive self-improvement* (2026-09-17), at 5:04: [https://dwarkesh.com/p/noam-brown](https://dwarkesh.com/p/noam-brown) — "it's just so expensive. You guys just did it over like a weekend. But that's one data point. Like we don't know how long it would take a single agent to solve not your strokes because we haven't done that experiment yet. And maybe we will, but I mean, that's also only one data point, right? And we want to do a thoro..."
  - dwarkesh, *Noam Brown – Agent swarms, alignment, & recursive self-improvement* (2026-09-17), at 19:05: [https://dwarkesh.com/p/noam-brown](https://dwarkesh.com/p/noam-brown) — "10,000 agents are at coordinating. We think it helped. We don't actually have good measurements of saying, like, oh yeah, this 10,000 agents led to a 2X speedup over 2,000 agents or something like that. It is actually, I would argue likely, maybe, I don't know about likely, but I think it is very possible that 10,00..."
- **[7]** (reported fact) Jellyfish's cost-per-PR analysis explicitly marks its revert-rate deltas as below the noise in the data rather than reporting them as a quality improvement.
  - ai-engineer, *Tokens Are the Cheap Part — Steve Jamison, Jellyfish* (2026-10-13), at 10:23: [https://www.youtube.com/watch?v=U7ZYBCcdJPg&t=622s](https://www.youtube.com/watch?v=U7ZYBCcdJPg&t=622s) — "One proxy for this is river reverts. Merged PRs that undo an earlier PR. The heaviest fifth started lowest before most of the token growth, and revert rates drop slightly for every group. Though these deltas are just slightly below the noise in the data. It's not evidence of a improvement here. However, more importa..."
- **[8]** (our inference) The apparent disagreement over whether harness scaffolding and state restoration help is better read as task dependence: both pay off only under specific conditions that the sources themselves identify, and neither generalises.
  - thoughtworks, *Are Harnesses Worth the Cost?* (2026-10-13): [https://martinfowler.com/articles/are-harnesses-worth-the-cost.html](https://martinfowler.com/articles/are-harnesses-worth-the-cost.html) — "A behavioral harness is not an automatic win for every model on every task. For Sol, running the harness throughout development added overhead without a detected acceptance benefit"
  - arxiv, *Returning to Development States: When Full Sandbox Snapshots Help Coding Agents* (2026-10-09): [https://arxiv.org/abs/2610.13841](https://arxiv.org/abs/2610.13841) — "For file-centric tasks, simpler representations and fresh re- tries are often enough. When progress lives in databases, services, installed dependencies, or other machine state out- side the repository, full snapshots become more compelling."
