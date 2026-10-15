# Technical demonstration — recording script (v2, screen capture)

**读法**：每个步骤先粘贴命令、等输出出现，再念下面那句英文。一句话对应一屏输出，不要提前念。
中文是操作提示，不念。

**时长**：旁白 607 词，15 条命令。145 词/分钟 + 每条约 4 秒停顿 ≈ **5:11**；慢到 135 词/分钟 ≈ 5:30，快到 155 ≈ 4:55。

**录前**：终端 18pt / 120 列，编辑器 16pt，各占半屏；命令先复制到记事本，录时粘贴不要现场打字；
每条命令先跑一遍预热；Substack 第三篇先开好标签页；关通知，不要露出账号页、API key、书签栏。

---

## 第 0 段 — 架构（0:00–0:18，无命令）

**操作**：编辑器打开 `SUBMISSION.md`，滚到 Architecture 的 mermaid 图，停住。

> This is the pipeline behind Harness Notes. Six stages, each with its own artifacts:
> collection, retained evidence, editorial decisions, drafting, mechanical checks, and a human
> approval gate. Everything after this is that diagram, running.

---

## 第 1 段 — 入口与组件（0:18–1:00）

### 1.1

```bash
ls run.sh workflows/*.sh collectors/*.sh processing/*.sh data/store.sh \
   editorial/*.sh content/*.sh review/*.sh publishing/*.sh reporting/*.sh
```

> Sixteen components. Three collectors, extraction, the evidence store, the date filter,
> selection, briefs, two writers, checks, packaging, reporting, and two workflows above them.

### 1.2

```bash
sed -n '3,5p' run.sh
```

> One entry point with three modes: a live run, a replay of a previous run's candidates, and
> packaging after approval.

### 1.3

```bash
bash data/store.sh get feed:7e289d45dfc4cd8f | jq -r '"\(.kind)  \(.publisher_id)  \(.title)\nversion \(.version_id[0:12])  text \(.text_path)"'
```

> Each component also runs on its own. This is the evidence store answering a `get` on one
> item. It is the only component allowed to read or write the index; everything else goes
> through these subcommands.

### 1.4

```bash
jq -c '{stage,status,input_count,output_count,elapsed_seconds,cost_usd,cost_is_estimate}' runs/20261015T014725Z-ny-next-day-live/logs/select_items-*.json
```

> And every invocation leaves a receipt: stage, status, counts in and out, elapsed time, and
> cost marked as an estimate, because the CLI reports list price rather than what I was billed.

---

## 第 2 段 — 一条 claim 追到已发布文章（1:00–1:48）

### 2.1

```bash
bash tools/trace_claim.sh runs/20261013T213636Z-podcasts-expanded 03-c9
```

**操作**：输出较长，边念边向上滚回顶部。

> One claim, traced end to end. Claim 03-c9: a practitioner reports AWS has roughly sixteen
> thousand APIs, too many to model as tools. The trace prints the claim in its brief, the lines
> that use it in the article and the script, the decision that accepted the source with the
> model's reason, and the stored version it cites. It resolves to two transcript segments from
> an MLOps Community episode, at thirty minutes forty-eight and fifteen minutes one.

### 2.2

**操作**：切到浏览器已发布的第三篇文章，`Cmd+F` 搜 `16,000`，再搜 `30:48`。

> Same claim in the published article, with the timestamp and a link a reader can open.

---

## 第 3 段 — 第二次运行与一次真实变更（1:48–2:36）

### 3.1

```bash
jq -r '.counts | "new=\(.new) changed=\(.changed) unchanged=\(.unchanged)"' runs/20261014T014037Z-second-live/summary.json
```

> The second live run: sixty-seven items re-observed, zero new, zero changed. Twenty-five
> transcripts were reused and nothing was transcribed again. Re-fetching a page is not evidence
> that it changed.

### 3.2

```bash
jq -r '.counts | "new=\(.new) changed=\(.changed) unchanged=\(.unchanged)"' runs/20261015T014725Z-ny-next-day-live/summary.json
```

> The next complete run, a day later in New York: twenty new, two changed.

### 3.3

```bash
sqlite3 data/evidence/evidence.sqlite "select version_id, first_run_id from versions where item_id='feed:7e289d45dfc4cd8f'"
```

> Here is one of the two. Two versions of the same item, each tagged with the run that first
> saw it. The older one is still retrievable.

### 3.4

```bash
diff data/assets/feed/d32c876482ebf166/{f7fb768c88d4,b4aca652c1f4}.txt | grep '^>' | fold -w 92 -s
```

> This is what changed: Simon Willison added an update crediting Piper and Sapling as prior
> art. The version hash covers title, URL, date, text and segments, and excludes retrieval
> time, so this registers as a change and a refetch does not.

---

## 第 4 段 — 故障恢复与一次标注的失败（2:36–3:20）

### 4.1

```bash
jq -r '.status + " :: " + .errors[0].message' runs/20261013T204414Z/logs/collect_sources-*.json
```

> The first live run genuinely failed, after four and a quarter hours of transcription: reading
> one element of PIPESTATUS resets it in bash 3.2. The sixty stored items survived, this
> receipt is labelled as written after the fact, and the next run recovered without
> re-transcribing.

### 4.2

```bash
jq '.coverage.collection.collectors, .coverage.coverage_complete' runs/20261014T005920Z-simulated-failure/summary.json
```

> The second failure is deliberate. The podcast collector exits one after its first source,
> marked simulated; the others finish, the workflow continues, and coverage is reported
> incomplete rather than quietly passing.

---

## 第 5 段 — 一处人工修正与一次政策修订（3:20–4:08）

### 5.1

```bash
jq -r 'select(.reason|test("Naresh Jain")) | .before[0:55] + "  ->  " + .after[0:55]' runs/20261013T213636Z-podcasts-expanded/corrections.jsonl | head -3
```

> The checks cannot catch everything. The model attributed a harness experiment to Martin
> Fowler, because the feed's author field names the site owner; the article names Naresh Jain.
> I fixed it across brief, article and script before approving, and all forty-three edits are
> stored with before and after text.

### 5.2

```bash
head -5 runs/20261013T230227Z-policy-v2/decisions_diff.md
```

> That review produced policy version two: judge a podcast on the whole episode, treat
> newsletter roundups as secondary, take authorship from the body. Replayed on identical
> evidence, fifty-two decisions held and fifteen moved.

---

## 第 6 段 — 架构取舍与系统终点（4:08–5:05）

### 6.1

```bash
sed -n '/^SCHEMA = /,/^"""/p' data/store.py | head -20
ls -l data/assets/feed/d32c876482ebf166/
```

> The tradeoff. The index is SQLite — items, versions, observations — but the text and
> transcript segments sit outside it as files named by the version hash, written once and never
> overwritten. Those are the two versions you just saw. The cost is duplication and a database
> that is not an archive on its own. What I get is a citation that names a file nobody can edit
> underneath it.

### 6.2

```bash
ls runs/20261013T213636Z-podcasts-expanded/package
```

> And the system stops here. It checks the approval against a fingerprint of the reviewed
> drafts, then hands over articles, scripts and source notes. Rendering and publishing are mine
> to do.

---

## 录制后（中文）

1. 确认 4–6 分钟，1080p 下终端文字可读。
2. 上传 YouTube（unlisted），标题 `Harness Notes — technical demonstration`。
3. 换掉 `SUBMISSION.md` 第 27 行的链接，并删掉 "shows rendered evidence cards, not a live
   screen capture" 那句。
4. `git add -A && git commit && git push`。

**时间不够或想补充时**：30 天窗口的排除记录可以插在 1.4 之后，一条命令一句话：
`head -2 runs/20261015T014725Z-ny-next-day-live/exclusions.jsonl | jq -c '{item_id,reason,detail}'`
→ “Items outside the thirty-day window are excluded with the reason and the exact dates.”

## 事实核对表（口误时以此为准）

| 说法 | 实际值 |
| --- | --- |
| 第二次 live run | 0 new / 0 changed / 67 unchanged，复用 25 份转写，转写 0 秒 |
| 纽约次日 run | 74 候选 / 67 抽取 / 20 new / 2 changed / 45 unchanged / 93 eligible，26 分 21 秒，$6.93 |
| 变化的那篇 | Simon Willison《Redesigning source control at Anthropic》，2419 → 2613 字符，两版都在库 |
| 1.4 那张 receipt | select_items，93 进 93 出，341 秒，$1.60（估算） |
| 证据库 | 96 items / 98 versions / 509 observations / 8 runs |
| 第一次 run 故障 | `PIPESTATUS[2]: unbound variable`，已存 60 条，下一次 run 零重转写恢复 |
| 模拟失败 | 播客采集器第一个源后退出 1，`coverage_complete: false` |
| 人工修正 | 共 43 处；Naresh Jain 归属修正横跨 brief / 文章 / 脚本 |
| 政策 v2 | 52 条决策不变，15 条变化，accept 27 → 30 |
| 溯源示例 | claim 03-c9 → MLOps 播客 s-0068 @ 30:48 与 s-0034 @ 15:01 |
