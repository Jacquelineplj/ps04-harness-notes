# Run index

Every run directory is created by `run.sh` and keeps its `run.json`, config and prompt
snapshots, receipts (`logs/`), intermediate JSONL artifacts, drafts and `summary.json`.
Nothing here is fictional; fixture-based checks run in a disposable directory
(`tests/run_example_checks.sh`).

| Run | Date (UTC) | Mode / label | Purpose | Outcome |
| --- | --- | --- | --- | --- |
| `20261013T204414Z` | 2026-10-13 | live | First live collection: 69 candidates, 60 items extracted and stored (4.25 h of podcast audio transcribed) | **failed** after the store upsert: `workflows/collect_sources.sh` hit a bash-3.2 `PIPESTATUS` bug before writing `corpus.jsonl`; recorded in `logs/collect_sources-*.json` (post-hoc receipt) and fixed in the workflow |
| `20261013T212217Z` | 2026-10-13 | live | First complete pass after the fix: 59 unchanged + 1 new item, 59 eligible, 23 accepted, 3 briefs, 3 articles, 3 scripts | **failed** the content checks on one blocking error: no podcast evidence was cited (every podcast episode in the corpus was off-topic and rejected). Recorded as the system refusing to publish without full input coverage |
| `20261013T213636Z-podcasts-expanded` | 2026-10-13 | live, label `podcasts-expanded` | **First live run (final).** Podcast discovery widened (keyword pre-filter, two more sources); 74 candidates, 65 items (9 new, 56 unchanged), 67 eligible from 16 publishers, 27 accepted, 3 briefs/articles/scripts, checks passed; human review (`editorial_review.md`, `corrections.jsonl`), approval, package | **ready_for_production** |
| `20261013T230227Z-policy-v2` | 2026-10-13 | replay, label `policy-v2`, `--until select` | Same candidate streams with editorial policy v2; 65/65 unchanged; decisions 30 accept / 36 reject / 1 defer vs 27/33/7 under v1 (`decisions_diff.md`) | inspection run (status `failed` by vocabulary: no drafts by design) |
| `20261014T005413Z-inject-withheld` | 2026-10-14 | replay, label `inject-withheld`, `--inject demo/withheld_candidate.jsonl`, `--until select` | Update demonstration: 65 unchanged + 1 new (the withheld Interconnects post), nothing re-transcribed; the injected item was judged and rejected as general opinion | inspection run |
| `20261014T005920Z-simulated-failure` | 2026-10-14 | live, label `simulated-failure`, `SIMULATE_COLLECTOR_FAILURE=podcasts`, `--until collect` | Labelled failure demonstration: podcast collector exits 1 after its first source (`simulated: true`), feeds/YouTube complete, workflow continues with 66 candidates; summary reports incomplete coverage | inspection run |

| `20261014T014037Z-second-live` | 2026-10-14 | live, label `second-live` | Second complete live pass: 74 candidates, 67 unchanged extracted items, 73 eligible, 27/45/1 accept/reject/defer, 3 briefs/articles/scripts. All 25 media transcripts reused. AI-assisted length edits logged in corrections.jsonl; checks pass with 5 editorial warnings | **ready_for_production** after Lingjie Pan explicitly reviewed and approved the edited drafts in this task; UTC dates differ, local New York date is still October 13 |

| `20261015T014725Z-ny-next-day-live` | 2026-10-15 UTC / **2026-10-14 New York** | live, label `ny-next-day-live` | Complete live run on a different New York date: 74 candidates, 67 extracted (20 new / 2 changed / 45 unchanged), 93 eligible, 35 accept / 50 reject / 8 defer, 3 briefs/articles/scripts. Brief validation: 25 exact quotes, 0 problems. Six model omissions explicitly deferred; source access/truncation limits preserved. AI edits and originals retained; final content checks 0 errors / 3 warnings. | **awaiting_review**, pipeline exit 0; no approval claimed. Time-zone proof and decision comparison included |
