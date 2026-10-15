# Technical demonstration — recording script (v2, screen capture)

**读法**：每一步先粘贴命令、等输出出现，再念下面那段英文。一段话对应一屏输出，不要提前念。
中文是操作提示，不念。每句都写成「屏幕上是什么 + 它意味着什么」，照念即可，不需要临场补充。

**时长**：旁白 672 词，14 条命令。145 词/分钟 + 每条约 4 秒停顿 ≈ **5:34**；慢到 135 词/分钟 ≈ 5:55，快到 155 ≈ 5:16。

**命令**：全部按顺序集中在 [demo_commands.sh](demo_commands.sh)，开在旁边整块复制粘贴即可；
`bash demo/demo_commands.sh` 可在录制前把全部命令跑一遍预热（只读，不改文件）。

**录前**：终端 18pt / 120 列，编辑器 16pt，各占半屏；录时粘贴不要现场打字；
每条命令先跑一遍预热；Substack 第三篇先开好标签页；关通知，不要露出账号页、API key、书签栏。

---

## 第 0 步 — 这是什么（0:00–0:26，无命令）

**操作**：编辑器打开 `SUBMISSION.md`，滚到 Architecture 的 mermaid 图，停住。

> Harness Notes is a publication for engineers building AI agent infrastructure; this is the
> pipeline behind it. It collects sources from the last thirty days, keeps the exact evidence
> it used, has a model decide what belongs in the edition and why, drafts the articles and
> scripts, checks them, then waits for me to approve. Everything after this is that diagram,
> running.

---

## 第 1 步 — 入口和组件（0:26–1:25）

### 1.1

```bash
ls run.sh workflows/*.sh collectors/*.sh processing/*.sh data/store.sh \
   editorial/*.sh content/*.sh review/*.sh publishing/*.sh reporting/*.sh
```

> Sixteen shell components, one responsibility each: three collectors, extraction, the evidence
> store, the thirty-day filter, selection, briefs, two writers, checks, packaging, reporting.
> The two workflows above them only sequence them and handle failures.

### 1.2

```bash
sed -n '3,5p' run.sh
```

> Three modes behind one entry point. A live run does everything. A replay reuses an earlier
> run's candidates, so I can change the policy and compare decisions without collecting again.
> Packaging runs only after I approve the drafts.

### 1.3

```bash
bash data/store.sh get feed:7e289d45dfc4cd8f | jq -r '"\(.kind)  \(.publisher_id)  \(.title)\nversion \(.version_id[0:12])  text \(.text_path)"'
```

> Components also run alone. Here the evidence store answers a `get` for one item: kind,
> publisher, title, the version in question, and the file holding its retained text. No other
> stage opens the database, so there is exactly one place where evidence can change.

---

## 第 2 步 — 一条论断追到已发布的文章（1:25–2:09）

### 2.1

```bash
bash tools/trace_claim.sh runs/20261013T213636Z-podcasts-expanded 03-c9
```

**操作**：输出较长，边念边向上滚回顶部，让每一节都在镜头里停一下。

> One claim traced end to end: claim nine of the third article. A practitioner reports AWS has
> roughly sixteen thousand APIs, too many to expose as individual tools. The trace prints the
> claim as the brief states it, the lines using it in the article and the script, the decision
> that accepted the source with the model's reason, and the two transcript segments it rests
> on, at thirty forty-eight and fifteen oh one.

### 2.2

**操作**：切到浏览器已发布的第三篇文章，`Cmd+F` 搜 `16,000`，再搜 `30:48`。

> The same claim in the published article, with the timestamp and a link, so a reader can go
> and hear the sentence I cite.

---

## 第 3 步 — 第二次运行与一次真实变更（2:09–3:18）

### 3.1

**操作**：两条命令连着粘贴，等两行结果都出来再念。

```bash
jq -r '.counts | "new=\(.new) changed=\(.changed) unchanged=\(.unchanged)"' runs/20261014T014037Z-second-live/summary.json
jq -r '.counts | "new=\(.new) changed=\(.changed) unchanged=\(.unchanged)"' runs/20261015T014725Z-ny-next-day-live/summary.json
```

> The second live run re-observed sixty-seven items: nothing new, nothing changed, twenty-five
> transcripts reused, no audio transcribed twice. Fetching a page again is not evidence that it
> changed. The next complete run, a day later, found twenty new items and two genuine changes.

### 3.2

```bash
sqlite3 data/evidence/evidence.sqlite "select version_id, first_run_id from versions where item_id='feed:7e289d45dfc4cd8f'"
```

> Here is one of those two. The store holds two versions of the same article, each tagged with
> the run that first saw it, and the earlier one is still retrievable.

### 3.3

```bash
diff data/assets/feed/d32c876482ebf166/{f7fb768c88d4,b4aca652c1f4}.txt | grep '^>' | fold -w 92 -s
```

> This is what changed: Simon Willison added an update crediting Piper and Sapling as prior
> art. The version id hashes title, URL, date, text and transcript but leaves out when I
> fetched the page, so re-downloading an unedited article keeps the same id, while a real edit
> like this one becomes a new version.

---

## 第 4 步 — 一次真实故障和一次标注的失败（3:18–4:02）

### 4.1

```bash
jq -r '.status + " :: " + .errors[0].message' runs/20261013T204414Z/logs/collect_sources-*.json
```

> The first live run genuinely failed, four and a quarter hours into transcription: in bash
> three point two, reading one element of PIPESTATUS resets the rest. The sixty stored items
> survived, this receipt was written afterwards and says so, and the next run recovered without
> transcribing anything twice.

### 4.2

```bash
jq '.coverage.collection.collectors, .coverage.coverage_complete' runs/20261014T005920Z-simulated-failure/summary.json
```

> The second failure is deliberate, to show what the summary does with one. The podcast
> collector exits non-zero after its first source, marked simulated; the others finish, the
> workflow continues, and coverage is reported incomplete rather than quietly passing.

---

## 第 5 步 — 一处人工修正与一次政策修订（4:02–4:43）

### 5.1

```bash
jq -r 'select(.reason|test("Naresh Jain")) | .before[0:55] + "  ->  " + .after[0:55]' runs/20261013T213636Z-podcasts-expanded/corrections.jsonl | head -3
```

> The checks cannot catch everything. The model credited a harness experiment to Martin Fowler
> because the feed's author field names the site owner; the article names Naresh Jain. I fixed
> that across brief, article and script before approving, and all forty-three edits are stored
> with before and after text.

### 5.2

```bash
head -5 runs/20261013T230227Z-policy-v2/decisions_diff.md
```

> The same review produced policy version two: judge a podcast on the whole episode, not
> sampled excerpts; treat newsletter roundups as secondary reporting; take authorship from the
> article body. Replayed on identical evidence, fifty-two decisions held and fifteen moved.

---

## 第 6 步 — 架构取舍与系统的终点（4:43–5:34）

### 6.1

**操作**：两条命令连着粘贴。

```bash
sed -n '/^SCHEMA = /,/^"""/p' data/store.py | head -20
ls -l data/assets/feed/d32c876482ebf166/
```

> The main tradeoff. The index is SQLite — items, versions, observations — but text and
> transcript segments live outside it as files named by the version hash, written once, never
> overwritten. Those are the two versions you just saw. The cost is duplicated text and a
> database that is not an archive alone; what I get is a citation pointing at a file nobody
> can edit.

### 6.2

```bash
ls runs/20261013T213636Z-podcasts-expanded/package
```

> The system stops here. It checks my approval against a fingerprint of the drafts I reviewed,
> then hands over articles, scripts and source notes. Rendering and publishing are mine to do.

---

## 录制后（中文）

1. 确认 4–6 分钟，1080p 下终端文字可读。
2. 上传 YouTube（unlisted），标题 `Harness Notes — technical demonstration`。
3. 换掉 `SUBMISSION.md` 第 27 行链接，并删掉 "shows rendered evidence cards, not a live
   screen capture" 那句。
4. `git add -A && git commit && git push`。

**还有富余时间想补的**（按顺序挑一个插在 1.3 之后，各约 25 秒）：

一、任一阶段的 receipt：
`jq -c '{stage,status,input_count,output_count,elapsed_seconds,cost_usd,cost_is_estimate}' runs/20261015T014725Z-ny-next-day-live/logs/select_items-*.json`
→ “Each stage also leaves a receipt. This is selection: ninety-three items in, ninety-three
decisions out, three hundred forty-one seconds, about a dollar sixty, and the cost is flagged
as an estimate because the tool reports list price, not what I was billed.”

二、30 天窗口的排除记录：
`head -2 runs/20261015T014725Z-ny-next-day-live/exclusions.jsonl | jq -c '{item_id,reason,detail}'`
→ “Anything published outside the thirty-day window is excluded with the reason and the exact
dates, so the window is auditable instead of implied.”

## 事实核对表（口误时以此为准）

| 说法 | 实际值 |
| --- | --- |
| 第二次 live run | 0 new / 0 changed / 67 unchanged，复用 25 份转写，转写 0 秒 |
| 纽约次日 run | 74 候选 / 67 抽取 / 20 new / 2 changed / 45 unchanged / 93 eligible，26 分 21 秒，$6.93 |
| 变化的那篇 | Simon Willison《Redesigning source control at Anthropic》，2419 → 2613 字节，两版都在库 |
| 1.4 那张 receipt | select_items，93 进 93 出，341 秒，$1.596（估算） |
| 证据库 | 96 items / 98 versions / 509 observations / 8 runs |
| 第一次 run 故障 | `PIPESTATUS[2]: unbound variable`，已存 60 条，下一次 run 零重转写恢复 |
| 模拟失败 | 播客采集器第一个源后退出 1，`coverage_complete: false` |
| 人工修正 | 共 43 处；Naresh Jain 归属修正横跨 brief / 文章 / 脚本 |
| 政策 v2 | 52 条决策不变，15 条变化，accept 27 → 30 |
| 溯源示例 | claim 03-c9 → MLOps 播客 s-0068 @ 30:48 与 s-0034 @ 15:01 |
