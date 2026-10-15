# Technical demonstration — recording script (v2, screen capture)

**读法**：每一步先粘贴命令、等输出出现，再念下面那段英文。口语稿，照着说就行，不用背。
中文是操作提示，不念。

**命令**：全部按顺序在 [demo_commands.sh](demo_commands.sh)，开在旁边整块复制粘贴；
录前先跑一次 `bash demo/demo_commands.sh` 预热（只读，不改任何文件）。

**时长**：旁白 655 词，11 条命令。145 词/分钟 + 每条约 4 秒停顿 ≈ **5:15**；慢到 135 词/分钟 ≈ 5:35，快到 155 ≈ 4:58。

**录前**：终端 18pt / 120 列，编辑器 16pt，各占半屏；录时粘贴不要现场打字；
Substack 第三篇先开好标签页；关通知，不要露出账号页、API key、书签栏。

---

## 第 0 步 — 这是什么（0:00–0:27，无命令）

**操作**：编辑器打开 `SUBMISSION.md`，滚到 Architecture 的 mermaid 图，停住。

> This is Harness Notes, a publication for people building AI agent infrastructure, and this
> is the pipeline that makes it. It collects what was published in the last thirty days, keeps
> the evidence it actually used, gets a model to decide what's worth covering and say why,
> writes the pieces, checks them, then stops and waits for me. Everything after this is that
> diagram, running.

---

## 第 1 步 — 入口（0:27–1:06）

**操作**：两条命令一起粘贴，等两段输出都出来再念。

```bash
ls run.sh workflows/*.sh collectors/*.sh processing/*.sh data/store.sh \
   editorial/*.sh content/*.sh review/*.sh publishing/*.sh reporting/*.sh
sed -n '3,5p' run.sh
```

> Sixteen separate programs, one job each, and two workflow scripts on top that just run them
> in order and decide what to do when one of them breaks. There's a single way in, with three
> modes: a normal run does everything; a replay reuses an earlier run's sources, so I can
> change the editorial policy and compare the decisions without collecting all over again; and
> packaging, which only happens after I've approved the drafts.

---

## 第 2 步 — 一条论断追回到源头（1:06–1:52）

### 2.1

```bash
bash tools/trace_claim.sh runs/20261013T213636Z-podcasts-expanded 03-c9
```

**操作**：输出较长，边念边向上滚回顶部，每一节在镜头里停一下。

> Let me trace one claim all the way back. This is claim nine from the third article: someone
> saying AWS has around sixteen thousand APIs, far too many to hand an agent as individual
> tools. The trace walks it backwards — the claim as the brief wrote it, where the article and
> the script use it, the decision that let the source in with the model's reason, and the two
> pieces of transcript it rests on.

### 2.2

**操作**：切到浏览器已发布的第三篇文章，`Cmd+F` 搜 `16,000`，再搜 `30:48`。

> And here's that same claim in the article I published, with the timestamp and a link, so a
> reader can go and listen to the sentence I'm quoting.

---

## 第 3 步 — 跑第二次会发生什么（1:52–3:11）

### 3.1

**操作**：两条命令一起粘贴。

```bash
jq -r '.counts | "new=\(.new) changed=\(.changed) unchanged=\(.unchanged)"' runs/20261014T014037Z-second-live/summary.json
jq -r '.counts | "new=\(.new) changed=\(.changed) unchanged=\(.unchanged)"' runs/20261015T014725Z-ny-next-day-live/summary.json
```

> Now the repeat runs. The second one looked at sixty-seven items again and found nothing new
> and nothing changed. It reused twenty-five transcripts and didn't transcribe a single thing
> twice. That's the point of keeping the evidence: downloading a page again doesn't mean the
> page changed. The run after that, a day later, did find twenty new items and two real
> changes.

### 3.2

```bash
sqlite3 data/evidence/evidence.sqlite "select version_id, first_run_id from versions where item_id='feed:7e289d45dfc4cd8f'"
```

> Here's one of those two. Same article, two versions now, each tagged with the run that first
> saw it, and the older one is still there.

### 3.3

```bash
diff data/assets/feed/d32c876482ebf166/{f7fb768c88d4,b4aca652c1f4}.txt | grep '^>' | fold -w 92 -s
```

> And this is what actually changed: Simon Willison added a note crediting Piper and Sapling.
> The version id comes from the title, the date, the text and the transcript, but deliberately
> not from when I downloaded it. So fetching an unchanged page again gets the same id and
> nothing new is stored, while a real edit like this one becomes a new version.

---

## 第 4 步 — 出错的时候（3:11–3:39）

```bash
jq -r '.status + " :: " + .errors[0].message' runs/20261013T204414Z/logs/collect_sources-*.json
```

> This one's my favourite, because it went wrong. The first live run died four hours into
> transcribing audio, on a bash quirk where reading one part of PIPESTATUS wipes the rest. The
> sixty items already stored survived, this receipt says plainly that I wrote it after the
> fact, and the next run picked up without transcribing anything twice.

---

## 第 5 步 — 我改了什么，政策又改了什么（3:39–4:14）

**操作**：两条命令一起粘贴。

```bash
jq -r 'select(.reason|test("Naresh Jain")) | .before[0:55] + "  ->  " + .after[0:55]' runs/20261013T213636Z-podcasts-expanded/corrections.jsonl | head -3
head -5 runs/20261013T230227Z-policy-v2/decisions_diff.md
```

> The automatic checks can't catch everything. The model credited a harness experiment to
> Martin Fowler, because the feed lists the site owner as the author, but the article is by
> Naresh Jain. I caught it in review and fixed it before approving, and all forty-three edits
> are saved with their before and after. That review is also where policy version two came
> from: replaying the identical evidence under it, fifty-two decisions stayed put and fifteen
> moved.

---

## 第 6 步 — 我会为之辩护的取舍（4:14–5:15）

### 6.1

```bash
ls -l data/assets/feed/d32c876482ebf166/
```

> Here's the tradeoff I'd defend. The index is a small database, but the text and transcripts
> sit next to it as ordinary files named after the version hash, written once and never touched
> again — these two are the versions you just saw. It costs me duplicated text, and the
> database on its own isn't the archive. What I get is a citation pointing at a file nobody can
> quietly edit underneath it. For a publication that promises you can go check the quote,
> that's the trade I want.

### 6.2

```bash
ls runs/20261013T213636Z-podcasts-expanded/package
```

> And this is where the system stops. It matches my approval against a fingerprint of the
> drafts I actually reviewed, hands over the articles, the scripts and the source notes, and
> leaves making the videos and publishing them to me.

---

## 录制后（中文）

1. 确认 4–6 分钟，1080p 下终端文字可读。
2. 上传 YouTube（unlisted），标题 `Harness Notes — technical demonstration`。
3. 换掉 `SUBMISSION.md` 第 27 行链接，并删掉 "shows rendered evidence cards, not a live
   screen capture" 那句。
4. `git add -A && git commit && git push`。

**时间有富余可以补的**（命令都在 demo_commands.sh 末尾，各约 25 秒）：

一、标注过的模拟采集失败，插在第 4 步之后：
`jq '.coverage.collection.collectors, .coverage.coverage_complete' runs/20261014T005920Z-simulated-failure/summary.json`
→ “I can also fail one on purpose. The podcast collector quits after its first source, flagged
as simulated; the other two finish, the run carries on, and the summary says coverage is
incomplete instead of quietly passing.”

二、任一阶段的 receipt，插在第 1 步之后：
`jq -c '{stage,status,input_count,output_count,elapsed_seconds,cost_usd,cost_is_estimate}' runs/20261015T014725Z-ny-next-day-live/logs/select_items-*.json`
→ “Every stage leaves one of these. Ninety-three items in, ninety-three decisions out, five
and a half minutes, about a dollar sixty — marked as an estimate, because that's list price,
not what I was billed.”

三、30 天窗口的排除记录，插在第 1 步之后：
`head -2 runs/20261015T014725Z-ny-next-day-live/exclusions.jsonl | jq -c '{item_id,reason,detail}'`
→ “Anything published outside the thirty-day window gets dropped with the reason and the dates
written down, so the window is something you can audit rather than take on trust.”

## 事实核对表（口误时以此为准）

| 说法 | 实际值 |
| --- | --- |
| 第二次 live run | 0 new / 0 changed / 67 unchanged，复用 25 份转写，转写 0 秒 |
| 纽约次日 run | 20 new / 2 changed / 45 unchanged，93 eligible，26 分 21 秒，$6.93 |
| 变化的那篇 | Simon Willison《Redesigning source control at Anthropic》，2419 → 2613 字节，两版都在库 |
| 第一次 run 故障 | `PIPESTATUS[2]: unbound variable`，4 小时 15 分转写后崩溃，已存 60 条，下次 run 零重转写 |
| 人工修正 | 共 43 处；Naresh Jain 归属修正横跨 brief / 文章 / 脚本 |
| 政策 v2 | 52 条决策不变，15 条变化，accept 27 → 30 |
| 溯源示例 | claim 03-c9 → MLOps 播客 s-0068 @ 30:48 与 s-0034 @ 15:01 |
| 证据库 | 96 items / 98 versions / 509 observations / 8 runs |
