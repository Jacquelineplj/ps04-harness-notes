# Problem Set 4 Student Submission

Complete this document with your project details and links. Keep the course instructions in [README.md](README.md) and the required contracts in [ARCHITECTURE.md](ARCHITECTURE.md).

**Student:** Lingjie Pan (lingjie_pan@fas.harvard.edu)  
**GitHub repository:** [Jacquelineplj/ps04-harness-notes](https://github.com/Jacquelineplj/ps04-harness-notes) (private; course-staff access must be granted)

## Topic and Audience

- **Publication name:** Harness Notes
- **Topic:** Engineering the harness around AI agents: context management, tool protocols (including MCP), sandboxing and permissions, memory, evaluation and benchmarks, multi-agent orchestration, and observability.
- **Audience and assumed knowledge:** Engineers and technical leads building agent products or agent infrastructure (coding agents, computer-use agents, agent SDKs and frameworks, MCP servers). They already understand tool calling, context windows, evals, and sandboxing basics and do not need the fundamentals explained.
- **Central question:** What changed this month in how AI agent harnesses are built, evaluated, and operated, and which of those changes should practitioners act on?
- **Scope and exclusions:** In scope: harness design (loops, context, compaction, memory, sub-agents), tool interfaces and protocols, safety rails inside the harness, agent evaluation methods and harness-sensitive benchmark results, production operation (tracing, cost, reliability), and research that measures a harness design choice. Excluded: model releases or leaderboard scores without a harness implication, consumer product news, funding and event marketing, beginner tutorials and prompt tips, policy news unless it changes what a harness must enforce. The full rules are in [config/editorial_policy.md](config/editorial_policy.md).
- **Reason for readers to return:** Every edition is a dated, evidence-linked digest with an explicit as-of date. Readers can see which sources changed the picture since the last edition, which vendor claims held up under scrutiny, and what to watch next; every claim links to the exact passage or timestamp that supports it.

## Published Series

The three articles are free and public. Unauthenticated HTTP checks returned 200 with the article titles and as-of dates on 2026-10-14 UTC. All three companion videos were produced in Google Vids and published unlisted on YouTube; each article links to its video, and each video description links to its article and numbered sources. Anonymous access and article cross-links were verified on 2026-10-14. [Production manifest and project links](runs/20261013T213636Z-podcasts-expanded/production/manifest.json); [verification results](runs/20261013T213636Z-podcasts-expanded/production/public_access_checks.json).

| Piece | Title | Substack article | YouTube video |
| --- | --- | --- | --- |
| 1 | The Harness Grew Up: What Changed in Agent Engineering This Month | [Read article](https://jacquelinepan.substack.com/p/the-harness-grew-up-what-changed) | [Watch video](https://youtu.be/4qUEXjaZM4Q) |
| 2 | Which Claims Held Up: Harnesses, Judges, and the Gap Between Passing and Working | [Read article](https://jacquelinepan.substack.com/p/which-claims-held-up-harnesses-judges) | [Watch video](https://youtu.be/bVXnraPti3g) |
| 3 | What To Build Next: State Ownership, Staged Autonomy, and the Audit Trail You Don't Have Yet | [Read article](https://jacquelinepan.substack.com/p/what-to-build-next-state-ownership) | [Watch video](https://youtu.be/pKNdJ5zOlJA) |

**Separate technical demonstration video:** [Watch the unlisted technical walkthrough](https://youtu.be/Xtke0Tbz18g). [Local recording script](demo/technical_demo_script.md) and [AI-narrated walkthrough manifest](demo/technical_demo_manifest.json). The 4:39 walkthrough shows rendered evidence cards, not a live screen capture; it records the second run before the subsequent human approval.

## Setup and Execution

Required tools (versions used): macOS with `/bin/bash` 3.2 (all scripts are bash-3.2 compatible), `jq` 1.7, Python 3.12, `uv` 0.8 (or `pip`), Node 24 (used by yt-dlp as its JavaScript runtime for YouTube), the Claude Code CLI 2.1 (`claude`) for model calls. `ffmpeg` is not required: audio is decoded by PyAV inside faster-whisper.

```bash
# 1. Python dependencies in a project-local virtual environment
uv venv .venv --python 3.12
uv pip install --python .venv/bin/python -r requirements.txt
#    (pip alternative: python3 -m venv .venv && .venv/bin/pip install -r requirements.txt)

# 2. Model provider (default: Claude Code CLI, headless; uses your Claude login, no key file)
claude --version                     # must be installed and logged in
#    Alternatives, credentials via environment variables only:
#    export LLM_PROVIDER=anthropic ANTHROPIC_API_KEY=...   (official anthropic SDK)
#    export LLM_PROVIDER=openai    OPENAI_API_KEY=...      (official openai SDK)

# 3. Deterministic component checks from examples/README.md (disposable evidence dir)
bash tests/run_example_checks.sh

# 4. Live run, then human review, then packaging
bash run.sh                          # ends in awaiting_review; prints summary JSON
#    ... review runs/RUN_ID/articles, video_scripts, decisions; write runs/RUN_ID/approval.json
bash run.sh --package runs/RUN_ID    # reruns checks, builds runs/RUN_ID/package/

# Replay and demonstration modes
bash run.sh --replay runs/RUN_ID --label policy-v2          # same candidates, current config snapshot
bash run.sh --replay runs/RUN_ID --inject withheld.jsonl    # introduce a previously withheld candidate
SIMULATE_COLLECTOR_FAILURE=podcasts bash run.sh --label simulated-failure   # labelled collector failure
bash tools/trace_claim.sh runs/RUN_ID 01-c1                 # trace a claim to its passage
```

Environment variables (all optional): `LLM_PROVIDER` (claude-cli | anthropic | openai), `LLM_MODEL` (override every stage), `WHISPER_MODEL` (default `small`), `MAX_TRANSCRIBE_SECONDS` (default 3600 per episode), `RETAIN_MEDIA` (set `0` to delete audio after transcription), `CAPTION_SLEEP_SECONDS`, `EXTRACT_REFRESH=1` (refetch written items in replay), `SIMULATE_COLLECTOR_FAILURE=<feeds|youtube|podcasts>[:after=N]`, `RUNS_DIR`, `EVIDENCE_DIR` (tests only). Credential variable names: `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`. No credential is written to any file, snapshot, or log.

Models and provider settings live in [config/models.json](config/models.json): selection uses `claude-sonnet-5` (bulk classification), briefs, articles and scripts use `claude-opus-5`, all through the Claude Code CLI with `--json-schema` structured output and our own system prompt (`--tools ""`, no filesystem access). The CLI reports a list-price cost estimate per call, which every receipt records as `cost_is_estimate: true`.

Configuration files: [config/project.json](config/project.json) (publication, topic, audience, central question, series questions, scope), [config/sources.json](config/sources.json) (19 sources, 16 publishers; each with `perspective`, `independence_note`, `max_items`, `lookback_days`, podcast `max_duration_seconds`), [config/editorial_policy.md](config/editorial_policy.md), and the four prompts in [prompts/](prompts/). `run.sh` validates them with `jq` before every run and snapshots them into `runs/RUN_ID/config` and `runs/RUN_ID/prompts`; every component reads only the snapshot.

## Architecture and Manual Handoffs

```mermaid
flowchart TD
    R[run.sh<br/>validate config, run.json, snapshots, store init] --> C[workflows/collect_sources.sh]
    R --> S[workflows/create_series.sh]
    C --> F[collectors/fetch_feeds.sh<br/>feedparser + httpx]
    C --> Y[collectors/fetch_youtube.sh<br/>yt-dlp metadata]
    C --> P[collectors/fetch_podcasts.sh<br/>feedparser enclosures]
    F --> M[candidates.jsonl]
    Y --> M
    P --> M
    M -->|pipe| E[processing/extract_content.sh<br/>trafilatura / captions json3 / faster-whisper<br/>assets in data/assets, media in data/media]
    E -->|pipe| D[(data/store.sh<br/>SQLite data/evidence)]
    D --> W[processing/filter_items.sh<br/>30-day window]
    W --> A[editorial/select_items.sh<br/>LLM: policy + prompt, batches of 6]
    A --> B[editorial/create_briefs.sh<br/>LLM: 3 briefs + deterministic quote validation]
    B --> N[content/write_articles.sh<br/>LLM per brief + mechanical Sources]
    B --> V[content/write_video_scripts.sh<br/>LLM per brief, reads the article]
    N --> K[review/check_content.sh<br/>fingerprint review_id]
    V --> K
    K --> H[Human: approval.json]
    H --> X[publishing/prepare_package.sh<br/>package/ + manifest + publication_links]
    R -.always last.-> Z[reporting/summarize_run.sh<br/>summary.json]
```

Helpers (each inside its owning component): every required `.sh` is a real bash entry point that validates arguments, resolves the run directory and executes the Python implementation next to it (for example `collectors/fetch_feeds.py`, `data/store.py`, `review/check_content.py`). Shared plumbing in [lib/](lib/): `common.sh` (paths, logging, exit codes), `receipt.py` (one receipt per invocation under `runs/RUN_ID/logs/`), `llm.py` (provider wrapper and per-call usage log `logs/llm_calls.jsonl`), `evidence.py` (reading retained assets, verbatim quote matching, version hash, source-note rendering), `sources.py` (feed fetching, URL canonicalisation, dates). Model calls happen in exactly four places: selection, briefs, articles, scripts (plus a cheaper "condense" call inside `create_briefs` for transcripts longer than 30k characters). Evidence is stored in `data/evidence/evidence.sqlite` (items, versions, observations) and only `data/store.sh` touches it; text and transcript segments are content-addressed files under `data/assets/<kind>/<item16>/<version12>.*`.

Manual handoffs after `awaiting_review`:

1. **Human editorial review.** Inputs: `runs/RUN_ID/articles/*.md`, `video_scripts/*.md`, `briefs.jsonl`, `decisions.jsonl`, `review.json` (warnings list what needs judgement). Output: `runs/RUN_ID/approval.json` with the current `review_id`, `decision`, `reviewer`, `reviewed_at`, `notes`; corrections to drafts are made in place and invalidate the fingerprint, so checks are rerun by `bash run.sh --package`.
2. **Video production (Google Vids or HeyGen).** Input: `package/NN-video-script.md` (scenes with Visual / On-screen text / Narration). Output: an MP4 per piece.
3. **Substack.** Input: `package/NN-article.md` (markers resolved to numbered references, Sources section, as-of and AI-assistance lines). Output: the article URL.
4. **YouTube.** Inputs: the MP4 and `package/NN-youtube-description.txt` (description with numbered source links and timestamps; add the Substack URL). Output: the video URL, which is then linked from the article.
5. **Record links** in `package/publication_links.json` and rerun `bash run.sh --package runs/RUN_ID`; links are preserved and reported in `summary.json` separately from production readiness.

## Evidence and Runs

All runs live under [runs/](runs/) (index in [runs/README.md](runs/README.md)). Each run directory holds `run.json`, the config and prompt snapshots, every receipt under `logs/` (one JSON per stage invocation plus `llm_calls.jsonl`), the JSONL artifacts named in ARCHITECTURE.md, the drafts, `review.json`, and `summary.json`. The evidence index is [data/evidence/evidence.sqlite](data/evidence/) (tables `items`, `versions`, `observations`; only `data/store.sh` touches it; `bash data/store.sh list` or `get ITEM_ID [VERSION_ID]` reads it). Retained text and timestamped transcript segments are committed under [data/assets/](data/assets/) (`<kind>/<sha256(item_id)[:16]>/<version_id[:12]>.txt|.segments.json`, 100 files, 2.9 MB). Original media: caption tracks and feed bodies are committed under [data/media/](data/media/); audio files are not (see [data/media/README.md](data/media/README.md) for retrieval via the `media_url` stored on each item).

Final published run: **[runs/20261013T213636Z-podcasts-expanded/](runs/20261013T213636Z-podcasts-expanded/)** — `decisions.jsonl` (67 decisions), `briefs.jsonl`, `articles/`, `video_scripts/`, `review.json`, `editorial_review.md`, `corrections.jsonl`, `approval.json`, `package/`.

| Run | Actual date | Run artifacts and logs | Elapsed time | Approximate cost |
| --- | --- | --- | --- | --- |
| First live run (attempt 1) | 2026-10-13 | [runs/20261013T204414Z/](runs/20261013T204414Z/) — 69 candidates, 60 items extracted and stored (14 caption tracks, 6 podcasts, 4.25 h transcribed), then the collection workflow crashed on a bash-3.2 `PIPESTATUS` bug before `corpus.jsonl`; recorded in `logs/collect_sources-*.json` (post-hoc receipt, labelled) | 38 min | $0 model cost (no model stage reached); local compute only |
| First live run (attempt 2) | 2026-10-13 | [runs/20261013T212217Z/](runs/20261013T212217Z/) — after the fix: 59 `unchanged` + 1 `new`, 59 eligible, 23 accepted, 3 briefs/articles/scripts; **content checks failed**: no podcast evidence cited because every podcast episode in the corpus was off-topic and rejected (`review.json`, one error) | 13 min | $4.07 (estimate, list price) |
| **First live run (final, published)** | 2026-10-13 | [runs/20261013T213636Z-podcasts-expanded/](runs/20261013T213636Z-podcasts-expanded/) — podcast discovery widened (keyword pre-filter, two more sources); 74 candidates, 65 items (9 `new`, 56 `unchanged`), 67 eligible from 16 publishers (38 feed / 15 YouTube / 14 podcast), 27 accepted, checks passed, human review and corrections, approved, packaged (`ready_for_production`) | 81 min to `awaiting_review` (plus human review and later packaging/link updates; `summary.json` wall time includes those updates) | $5.12 (estimate, list price; 23 model calls, 1.16 M input tokens) |
| Policy revision replay | 2026-10-13 | [runs/20261013T230227Z-policy-v2/](runs/20261013T230227Z-policy-v2/) — `--replay` of the final run with policy v2, stopped after selection; 65/65 `unchanged`; decisions 30/36/1 vs 27/33/7; diff in `decisions_diff.md` | 5 min | $1.08 (estimate) |
| Injected-item replay | 2026-10-14 (UTC) | [runs/20261014T005413Z-inject-withheld/](runs/20261014T005413Z-inject-withheld/) — `--replay` of the final run plus [demo/withheld_candidate.jsonl](demo/withheld_candidate.jsonl) (a real Interconnects post deliberately kept out of `config/sources.json`); `changes.jsonl`: 65 `unchanged`, 1 `new`; extraction reused 65 items and transcribed nothing; the injected item was judged by the policy (rejected as general opinion) | 5 min | $1.09 (estimate) |
| Simulated collector failure | 2026-10-14 (UTC) | [runs/20261014T005920Z-simulated-failure/](runs/20261014T005920Z-simulated-failure/) — `SIMULATE_COLLECTOR_FAILURE=podcasts`, `--until collect`: the podcast collector emitted 3 candidates from its first source, then exited 1 with an error marked `simulated: true`; feeds and YouTube completed; the workflow continued (66 candidates, 73 eligible) and `summary.json` reports `coverage_complete: false`, the failed collector and the simulated flag | 5 min | $0 (no model stage) |
| Second live run | 2026-10-14 UTC | [runs/20261014T014037Z-second-live/](runs/20261014T014037Z-second-live/) — 0 new / 0 changed / 67 unchanged; 73 eligible; 27 accepted; 3 briefs/articles/scripts; checks pass with 5 editorial warnings; human approved and packaged (`ready_for_production`) | 15 min 18 sec to awaiting review | $5.20 (estimate, list price) |

Costs are the Claude Code CLI's own list-price estimates recorded per call (`cost_is_estimate: true` in every receipt); the subscription is not billed per token, so the true marginal cost is unknown and the summary reports it under `costs.estimated_usd` with `known_usd: 0`. Local transcription and all other stages are reported at cost 0 with `cost_basis: local compute`.

**Second-live-run comparison.** Both runs started on October 13 in America/New_York; their actual UTC execution dates are October 13 and 14. They are different UTC dates, not runs separated by 24 hours. The second run found no new or changed extracted evidence and reused all 25 media transcripts. Intervening runs had grown the store, so 73 items were eligible versus 67 in the first final run. Under policy v2, 27 were accepted, 45 rejected, and 1 deferred. The new briefs cite 3 distinct podcasts versus 1 previously, and shift piece 1 toward the harness experiment and piece 2 toward conditional snapshot results. See [decision comparison](runs/20261014T014037Z-second-live/decisions_diff.md). The validation stage dropped an unlocatable claim from brief 02. Lingjie Pan then explicitly reviewed and approved the edited drafts in this task; the run is packaged as `ready_for_production`.

**What changed between runs.** Attempt 1 discovered and stored everything; attempt 2 added one newly published article (`feed:…` in its `changes.jsonl`) and re-observed 59 items unchanged, which shows the version hash is stable across re-fetches of written pages; the final run added 9 podcast episodes as `new` and reused 56 items (19 media transcripts were not re-transcribed; `extract_content` receipt: `reused: 56, fetched: 18`). The policy replay observed 65/65 unchanged. Unknown or estimated costs are listed per run in `summary.json → costs`.

**Duplicate handling.** `changes.jsonl` of attempt 2 and of the final run show `unchanged` for every re-observed item and `new` only for genuinely new material; `data/store.sh` was also verified against `examples/` with `tests/run_example_checks.sh` (duplicate input lines and refreshed `retrieved_at` produce `unchanged`, a changed transcript produces one `changed` version while the earlier version stays retrievable). No podcast/YouTube pair of the same recording occurred in the window; the reconciliation rule (`duplicates.jsonl`, `aliases`) stayed empty and is documented in `processing/extract_content.py`.

**Date-window checks.** Every run's `exclusions.jsonl` records the items outside the 30-date window with `outside_window` and the exact dates (for example a 22 August and a 4 September post in the final run; window 14 September to 13 October). The fixture check covers `unknown_date`, `future_date` and `invalid_date`.

**Collection failure and recovery.** Attempt 1 is a genuine failure (collector outputs preserved, store populated, workflow aborted, receipt written after the fact and labelled `written_post_hoc`), recovered by attempt 2 without re-transcribing anything. Attempt 2 is a genuine *editorial* failure: the pipeline refused to publish without podcast evidence instead of inventing it. The `simulated-failure` run demonstrates a labelled collector failure (`SIMULATE_COLLECTOR_FAILURE=podcasts`): `collection_status.json` records the podcast collector's exit 1 and `simulated: true`, its receipt carries the simulated error, the other collectors' results were kept, and `summary.json` lists `collector:podcasts` under `failed_or_incomplete_stages` with `coverage_complete: false`. Every OpenAI article page returned HTTP 403 in all runs; those items are recorded as inaccessible in the extraction receipts rather than silently dropped.

**Claim trace** (`bash tools/trace_claim.sh runs/20261013T213636Z-podcasts-expanded 03-c9`): claim `03-c9` ("a practitioner reports AWS has roughly 16,000 APIs, too many to model as tools, pushing them toward code-mode execution that is itself hard for humans to review", type `source_claim`) → brief 03 → editorial decision `accept` for pieces 01/02/03 on item `podcast:8d8927fb57f7e934` (MLOps Community, *AWS Has 16,000 APIs. Can MCP Handle It?*, published 2026-09-28) → stored version `72917d775f28…` → transcript segments `s-0068` (30:48–31:17) and `s-0034` (15:01–15:29) in `data/assets/podcast/93cf1193e6ac377f/72917d775f28.segments.json` → cited in `articles/03.md` ("noted at 30:48 … conceded at 15:01") and resolved in `package/03-sources.md` with the episode link and timestamps.

## Editorial Review

Policy and prompts used: [config/editorial_policy.md](config/editorial_policy.md) (v2, current) and [prompts/](prompts/); the v1 policy that produced the published run is preserved in [runs/20261013T213636Z-podcasts-expanded/config/editorial_policy.md](runs/20261013T213636Z-podcasts-expanded/config/editorial_policy.md), the v2 snapshot in [runs/20261013T230227Z-policy-v2/config/editorial_policy.md](runs/20261013T230227Z-policy-v2/config/editorial_policy.md).

The review of four accepted and five rejected or deferred items, comparing the AI's reasons with my judgement, is in [runs/20261013T213636Z-podcasts-expanded/editorial_review.md](runs/20261013T213636Z-podcasts-expanded/editorial_review.md). Summary: I agreed with seven of nine decisions, partly with one, and disagreed with one — the deferral of the Latent Space episode with an Anthropic Claude Code engineer, which the selection stage judged from sampled transcript excerpts that did not show harness content.

**Policy revision (v1 → v2)** — three changes, each traced to a reviewed decision or correction: (1) audio/video items are judged on the whole episode when the title, guest or description names a harness product; (2) newsletter roundups are secondary reporting and deferred by default; (3) authorship is taken from the article body, not from feed-level author fields. Effect on the same evidence (`decisions_diff.md`): 52 of 67 decisions identical; the Claude Code episode moved defer → accept (01, 03); two more deferrals became accepts and three became rejects; the rest are piece reassignments. The replay was stopped after selection (`--until select`) so the comparison isolates the affected stage.

**Factual corrections** (all 43 recorded with before/after text and reasons in [corrections.jsonl](runs/20261013T213636Z-podcasts-expanded/corrections.jsonl)): the harness experiment on martinfowler.com was attributed to Martin Fowler by the model because the feed's author field names the site owner; the retained text identifies Naresh Jain, so briefs, article 02 and script 02 were corrected. Article 03 referred to "our last edition", which does not exist; it now refers to piece 02. Articles 02/03 and script 02 were trimmed to the length targets without removing any claim or marker. Two quotes from an arXiv PDF were normalised to the retained wording (line-break hyphenation) by the validator and checked by hand.

**Approval evidence:** [review.json](runs/20261013T213636Z-podcasts-expanded/review.json) (passed, 0 errors, 5 warnings all reviewed) and [approval.json](runs/20261013T213636Z-podcasts-expanded/approval.json) carry the same `review_id`; `bash run.sh --package` recomputed the fingerprint before building [package/](runs/20261013T213636Z-podcasts-expanded/package/).

## Reflection

**One insight the system produced.** Piece 02's central conditional was not in any single source: a Thoughtworks-hosted experiment found a behavioural harness added only cost for a frontier model but took a cheaper model from 3/10 to 10/10; the sandbox-snapshot paper found full-machine restoration only helps when progress lives outside the repository; Microsoft's skills-over-MCP post found a smaller initial context is not automatically a cheaper conversation. Read together they say harness machinery pays exactly when it supplies information the model or the repository does not already have. The brief stage produced that synthesis as an explicit `inference` claim with three locators, and the article labels it as interpretation.

**One editorial failure or limitation.** The system attributed Naresh Jain's experiment to Martin Fowler. The cause was structural: the feed collector copies the feed-level `author`, the selection prompt saw "Martin Fowler" in the metadata header before the text, and every later stage inherited the reason. The mechanical checks cannot catch a semantically wrong attribution, only an unresolvable quote; the human review caught it. A second limitation is that selection judges long transcripts from sampled excerpts, which deferred the single most relevant podcast episode; policy v2 narrows that, but the real fix is to let the selection stage read a condensed full transcript, which is the next improvement I would make.

**Next improvement.** Move the transcript-condensing call (currently only in `create_briefs`) in front of selection so every media item is judged on a model-written excerpt map of the whole episode, and store that map as a retained asset so it is cited the same way as segments.

**Architectural tradeoff.** The evidence store is a SQLite index of *records* plus content-addressed asset files, rather than storing text in the database. Version ids hash the title, URL, date, text and segments and exclude retrieval time, so a refetched page that has not changed is `unchanged`, a re-upload with a new date is a new version with the old one still retrievable, and every citation names a version whose file cannot be overwritten. The cost is duplication when metadata changes (a retitled video stores a second copy of an identical transcript) and a reuse rule that must be explicit (`extract_content` reuses media transcripts through `store.sh list` and re-transcribes only when the stored transcript was capped shorter than now allowed). For a publication whose value is that every claim can be traced to an exact passage, immutable versioned assets are the right side of that tradeoff.
