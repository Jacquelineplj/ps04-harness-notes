# Technical demonstration — recording script (v2, screen capture)

**用途**：4–6 分钟技术演示视频的逐段稿。英文是逐字念的旁白，中文是操作提示。
目标时长 **5:47**（旁白 728 词：按 145 词/分钟约 5:47，讲得慢一些按 135 词/分钟约 6:10，两种语速都在 4–6 分钟内）。
这一版是**真实录屏**，与已发布的 `Xtke0Tbz18g`（渲染卡片版）不同；录完后把
`SUBMISSION.md` 第 27 行的技术演示链接换成新视频。

---

## 录制前准备（中文）

- 终端字号调到 18pt 以上，窗口宽度至少 120 列；编辑器字号 16pt 以上。两者各占半屏。
- `cd /Users/panpanlj/Desktop/harvard.nosync/mit1.125/ps04-main`，先把下面每条命令跑一遍预热，
  确认输出和稿子一致（Substack 页面也先在浏览器里打开好标签页）。
- 关掉通知；不要出现任何账号页、API key、`.env`、浏览器书签栏。
- 录屏工具：QuickTime「新建屏幕录制」或 `Cmd+Shift+5`，记得勾选麦克风。
- **把本文件里的命令先复制到一个记事本窗口**，录制时直接粘贴回车，不要现场打字——
  每段停顿控制在 5 秒内，全片才稳定在 6 分钟以内。
- 每段念完稍停 1 秒再粘贴下一条命令，后期好剪。

**本段要念的开场不需要画面切换，直接从仓库根目录的终端开始。**

---

## 1. 0:00–0:33 — What this is and how it is separated

**操作**：先显示编辑器里的 `SUBMISSION.md`，滚到 Architecture 那张 mermaid 图，停住。

> Harness Notes is a publication for engineers who build AI agent infrastructure. This video
> is about the system that produces it, not the articles. The architecture separates six
> concerns: collection, retained evidence, editorial decisions, drafting, mechanical checks,
> and a human approval gate before packaging. That separation is the point: I can inspect why
> one source was accepted, or repair one stage, without silently changing the evidence behind
> an article that was already reviewed.

---

## 2. 0:33–1:15 — Entry point and the contracts between stages

**操作**：终端执行，输出很短，念完刚好滚完。

```bash
ls run.sh workflows/*.sh collectors/*.sh processing/*.sh data/store.sh \
   editorial/*.sh content/*.sh review/*.sh publishing/*.sh reporting/*.sh
sed -n '2,7p' run.sh
ls runs/20261015T014725Z-ny-next-day-live/logs | head -5
```

> Sixteen components, one entry point. `run.sh` validates the configuration, snapshots the
> config and prompts into the run directory, records the execution date, and calls two
> workflows. Collection runs three collectors, extracts text or timestamped transcripts,
> updates the evidence store, and applies the thirty-day window. The series workflow turns
> eligible evidence into decisions, briefs, articles and scripts, then runs the content checks.
> Every stage runs independently, reads JSON Lines on standard input, and writes a receipt.
> Only `data/store.sh` may touch the evidence index.

---

## 3. 1:15–2:06 — Trace one source into a published claim

**操作**：跑溯源命令，输出较长，边说边向上滚动；念到最后一句时切到浏览器里已发布的第三篇文章，
用 `Cmd+F` 搜 `16,000` 和 `30:48` 高亮给镜头看。

```bash
bash tools/trace_claim.sh runs/20261013T213636Z-podcasts-expanded 03-c9
```

> Here is one claim traced end to end. Claim 03-c9 says a practitioner reports AWS has roughly
> sixteen thousand APIs, too many to model as tools, pushing them toward code-mode execution
> that is hard to review. The trace shows the claim in its brief, the lines using it in the
> article and the script, and the decision that accepted the source, with the model's reason.
> The source is an MLOps Community episode, and the claim resolves to two transcript passages:
> thirty minutes forty-eight seconds, and fifteen minutes one second. Here is that same claim
> in the published article, with the timestamp and a link readers can check.

---

## 4. 2:06–3:01 — The second run, reuse, and a real change

**操作**：三条命令。第二条的 `changed` 两行是重点，第三条的 diff 是全片最有说服力的画面，
diff 输出停久一点。

```bash
jq -r '.counts | "new=\(.new) changed=\(.changed) unchanged=\(.unchanged)"' runs/20261014T014037Z-second-live/summary.json
jq -r '.counts | "new=\(.new) changed=\(.changed) unchanged=\(.unchanged)"' runs/20261015T014725Z-ny-next-day-live/summary.json
sqlite3 data/evidence/evidence.sqlite "select version_id, first_run_id from versions where item_id='feed:7e289d45dfc4cd8f'"
diff data/assets/feed/d32c876482ebf166/{f7fb768c88d4,b4aca652c1f4}.txt | grep '^>' | fold -w 92 -s
```

> The second live run re-observed sixty-seven items: zero new, zero changed, twenty-five
> transcripts reused, nothing transcribed again. Re-fetching a page is not evidence that it
> changed. The next complete run, a day later in New York, found twenty new items and two
> changed. Here is one. Simon Willison's post on source control at Anthropic gained an update
> paragraph crediting Google's Piper and Meta's Sapling as prior art. The version hash covers
> title, URL, date, text and segments and excludes retrieval time, so this registered as
> changed rather than as noise. Both versions are retained, so an article citing the first one
> still resolves to the words that were actually there.

---

## 5. 3:01–3:55 — Failure recovery, and a failure the system refused to hide

**操作**：两条命令。第一条是真实故障的事后 receipt，第二条是标注过的模拟失败。

```bash
jq -r '.status + " :: " + .errors[0].message' runs/20261013T204414Z/logs/collect_sources-*.json
jq '.coverage.collection.collectors, .coverage.coverage_complete' runs/20261014T005920Z-simulated-failure/summary.json
```

> The first live run genuinely failed. After four and a quarter hours of transcription the
> workflow crashed on a bash 3.2 quirk: reading one element of PIPESTATUS resets it. The sixty
> stored items survived, the failure sits in a receipt labelled as written after the fact, and
> the next run recovered without re-transcribing anything. The second example is deliberate.
> With the simulated-failure flag the podcast collector exits one after its first source. The
> others finish, the workflow continues, and the summary reports coverage incomplete, naming
> the failing collector and marking it simulated. The store still holds older podcast evidence,
> so finding podcasts in the corpus would not prove this collection worked.

---

## 6. 3:55–4:46 — One human correction and one policy revision

**操作**：第一条命令显示修正记录；第二条打开政策对比文件，滚到统计那一行。

```bash
jq -r 'select(.reason|test("Naresh Jain")) | .before[0:55] + "  ->  " + .after[0:55]' runs/20261013T213636Z-podcasts-expanded/corrections.jsonl | head -3
head -5 runs/20261013T230227Z-policy-v2/decisions_diff.md
```

> Mechanical checks cannot catch everything. The model attributed a harness experiment to
> Martin Fowler because the feed's author field names the site owner; the article text names
> Naresh Jain. I corrected that across the brief, the article and the script before approving,
> and all forty-three edits are stored with before and after text and a reason. The policy
> revision came out of the same review. Version two judges a podcast on the whole episode
> rather than sampled excerpts, treats newsletter roundups as secondary reporting, and takes
> authorship from the article body. Replaying identical evidence left fifty-two decisions
> unchanged and moved fifteen, including an episode version one had deferred.

---

## 7. 4:46–5:47 — The storage tradeoff, and where the system stops

**操作**：先显示 `data/store.py` 的表定义（`SCHEMA` 那段），再显示一个资产路径，
最后显示 package 目录和 `publication_links.json`。

```bash
sed -n '/^SCHEMA = /,/^"""/p' data/store.py | head -24
ls runs/20261013T213636Z-podcasts-expanded/package
```

> The main tradeoff is here. The index is SQLite, holding items, versions and observations,
> but the text and transcript segments live outside it as content-addressed files named by the
> version hash, written once and never overwritten. The cost is duplication when metadata
> changes, and the database alone is not an archive: the asset files must travel with it. In
> return, every citation names a version whose file cannot be edited underneath it. For a
> publication whose value is that a claim traces to an exact passage, that is the right side of
> the trade. The system stops at this package. It checks the approval against a fingerprint of
> the reviewed drafts, then hands over the articles, scripts and source notes. Rendering and
> publishing stay manual, and published links are reported separately from readiness.

---

## 超时应急（中文）

讲得慢（135 词/分钟）时总长约 6:10，会超出上限。两处可直接整句删掉，不影响作业要求覆盖：

1. 第 1 段第二句：“This video is about the system that produces it, not the articles.”（12 词）
2. 第 5 段最后一句：“The store still holds older podcast evidence, so finding podcasts in the corpus
   would not prove this collection worked.”（21 词）

删掉这两句后，135 词/分钟约 5:55，145 词/分钟约 5:33。

---

## 录制后（中文）

1. 检查成片时长在 4–6 分钟之间，终端文字在 1080p 下可读。
2. 上传 YouTube（unlisted 即可），标题建议 `Harness Notes — technical demonstration`。
3. 把 `SUBMISSION.md` 第 27 行的技术演示链接换成新视频，并把那句
   "shows rendered evidence cards, not a live screen capture" 改成实际情况。
4. `git add -A && git commit && git push`。

## 事实核对表（录制时如果口误，以此为准）

| 说法 | 实际值 |
| --- | --- |
| 第二次 live run | 0 new / 0 changed / 67 unchanged，复用 25 份转写，转写 0 秒 |
| 纽约次日 run | 74 候选 / 67 抽取 / 20 new / 2 changed / 45 unchanged / 93 eligible，26 分 21 秒，$6.93 |
| 变化的那篇 | Simon Willison《Redesigning source control at Anthropic》，2419 → 2613 字符，两个版本都在库 |
| 证据库 | 96 items / 98 versions / 509 observations / 8 runs |
| 第一次 run 故障 | `PIPESTATUS[2]: unbound variable`，已存 60 条，下一次 run 零重转写恢复 |
| 模拟失败 | 播客采集器第一个源后退出 1，`coverage_complete: false` |
| 人工修正 | 共 43 处；Naresh Jain 归属修正横跨 brief / 文章 / 脚本 |
| 政策 v2 | 52 条决策不变，15 条变化，accept 27 → 30 |
| 溯源示例 | claim 03-c9 → MLOps 播客 s-0068 @ 30:48 与 s-0034 @ 15:01 |
