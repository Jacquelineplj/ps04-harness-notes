# Harness Notes — technical demonstration recording script

Target: 4–6 minutes. Record the screen with your own narration at approximately
140 words per minute. The three audience videos must separately use Google Vids
or HeyGen. This document is a recording aid, not a completed video.

Before recording, finish the second run, insert its measured results into the
marked paragraph, and open a published article when available. Do not describe
an unpublished package as a published article. Enlarge the editor and terminal
so individual records are readable. Keep account pages and credentials off screen.

## 0:00–0:40 — Purpose and architecture

Show: `SUBMISSION.md`, Topic and Audience, then Architecture.

Narration:

“Harness Notes is a publication for engineers building AI agent infrastructure.
It asks what changed in agent harness design, which claims survive scrutiny,
and what engineers should build or watch next. The output is a connected
three-piece series, with an article and a video script generated from the same
brief for each piece. The architecture separates collection, retained evidence,
editorial decisions, writing, review, and the production handoff. That separation
lets me inspect a decision or repair one stage without silently replacing the
evidence behind an already reviewed article.”

## 0:40–1:25 — Entry point and contracts

Show: `run.sh`, `workflows/collect_sources.sh`, `workflows/create_series.sh`.

Narration:

“run.sh snapshots the configuration and prompts and records the execution date.
The collection workflow gathers feeds, YouTube items, and podcasts, extracts
text or timestamped transcripts, upserts the evidence store, and applies the
thirty-day publication window. JSON Lines streams connect the components.
Each stage writes a receipt describing counts, errors, timing, and available
cost information. The series workflow asks the model to make explicit accept,
reject, or defer decisions, then creates three briefs, articles, and scripts.
Content checks run before a separate human approval gate. Packaging checks that
the approval matches the fingerprint of the current reviewed inputs.”

## 1:25–2:25 — Trace a claim into retained evidence

Run:

```bash
bash tools/trace_claim.sh runs/20261013T213636Z-podcasts-expanded 03-c9
```

Show: terminal output, then `package/03-article.md`; use the published page if ready.

Narration:

“Here is a complete trace for claim 03-c9. The third article discusses the scale
of the AWS tool surface and the difficulty of reviewing generated code-mode
operations. The trace shows the claim in the brief, its uses in the article and
video script, and the editorial decision that accepted the source. The source is
the MLOps Community episode ‘AWS Has 16,000 APIs. Can MCP Handle It?’ The retained
version has both a text file and a segment file. At 30 minutes 48 seconds, the
speaker describes roughly sixteen thousand APIs. A separate segment at 15
minutes 1 second supports the point about reviewing generated Python. These are
two distinct pieces of support. Keeping their exact passages prevents a broad
summary from pretending that one quote establishes both claims.”

## 2:25–3:10 — Second run and duplicate handling

Show: the second live run's `run.json`, `summary.json`, and `changes.jsonl`.

Narration to complete from actual results:

“The first final live run uses October 13 UTC. The second live run uses October
14 UTC; both started on October 13 in New York. These are different UTC execution
dates, rather than a claim of twenty-four hours between runs. [Read the second
run's actual new, changed, and unchanged counts here.] An unchanged observation
preserves the existing content version. A changed item creates another retained
version, rather than overwriting the earlier evidence. [Name one actual change
in selection or synthesis, or state plainly that there was no new evidence.]
The separately labelled injected replay is an update demonstration, not a
substitute for live collection.”

## 3:10–3:50 — Failure visibility

Show: `runs/20261014T005920Z-simulated-failure/summary.json`, especially
`coverage.collection.collectors` and `coverage.coverage_complete`.

Narration:

“This is a deliberately labelled failure test. The podcast collector stops
after its first source, while feeds and YouTube complete. The workflow preserves
usable results, and the summary says coverage is incomplete. The store may still
contain older podcast evidence, so merely finding podcasts in the corpus would
not prove this collection succeeded. Reporting current collector status alongside
retained evidence makes that distinction visible. This run stops after collection
and is not presented as a completed publication run.”

## 3:50–4:35 — Editorial correction and policy revision

Show: first run's `corrections.jsonl`, then
`runs/20261013T230227Z-policy-v2/decisions_diff.md`.

Narration:

“One saved editorial correction changes the harness experiment attribution from
Martin Fowler to Naresh Jain. The hosting site and the author are different;
the correction was applied across the brief, article, and script before approval.
Policy version two also clarified how to judge practitioner reports and podcast
episodes. Replaying the same evidence gave thirty accepted items instead of
twenty-seven, with fifty-two decisions identical and fifteen changed. Those
changes include assignments to individual pieces, not just accept-versus-reject
flips. The saved reasons let a reviewer evaluate whether the revised policy
improved judgment.”

## 4:35–5:15 — Architectural tradeoff and handoff

Show: `data/store.py`, a retained asset path, then the first run's `package/manifest.json`.

Narration:

“The main storage tradeoff is SQLite for the index and content-addressed files
for retained text and transcript segments. This keeps the index compact and
makes evidence easy to inspect with ordinary tools. It also means the database
alone is not a complete archive: the referenced asset files must travel with it.
The production package contains numbered citations, source notes, article text,
scene-based scripts, and YouTube descriptions. Rendering and publishing are
separate operations. The submission must contain real accessible links; passing
checks or producing a package does not mean anything has been published.”
