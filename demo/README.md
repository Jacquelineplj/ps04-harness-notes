# Demonstration fixture (real, labelled)

`withheld_candidate.jsonl` is one real, dated candidate from a source that is deliberately
**not** in `config/sources.json` (the Interconnects newsletter). It was collected on the
date in its `retrieved_at` field with `collectors/fetch_feeds.sh` and withheld from the
live runs so that a labelled replay can demonstrate update behaviour:

```bash
bash run.sh --replay runs/<LIVE_RUN_ID> --inject demo/withheld_candidate.jsonl --label inject-withheld
```

The replay copies the live run's candidate streams, appends this record as
`candidates/injected.jsonl`, and runs extraction, storage, filtering and the editorial
stages again. Expected store result: every previously seen item `unchanged`, the injected
item `new`. This is not a fictional fixture; the item is genuine evidence and is treated
as such by the editorial policy.

The recorded replay is [runs/20261014T005413Z-inject-withheld/](../runs/20261014T005413Z-inject-withheld/).
