# TODO — 完成状态（2026-10-14 UTC）

- [x] 三篇 Substack 文章已免费公开发布，未发送订阅邮件；匿名访问检查通过。
- [x] 三个文章链接已回填 `package/publication_links.json` 和 `SUBMISSION.md`。
- [x] 第二次完整 live run：`runs/20261014T014037Z-second-live/`；0 new、0 changed、67 unchanged。
- [x] 第二次 run 的稿件已缩短到长度目标；内容检查通过（0 errors / 5 warnings）。
- [x] Lingjie Pan 在本次任务中明确复核批准；第二次 run 已打包为 `ready_for_production`。
- [x] 运行表、运行索引和决策对比已更新。两次 run 是不同 UTC 日期，但纽约本地日期相同。
- [x] 私有 GitHub 仓库已创建：https://github.com/Jacquelineplj/ps04-harness-notes 。
- [x] 4:39 AI 配音技术演示已生成并上传到 YouTube 草稿；是证据卡片演示，不是实时屏幕录制。
- [ ] 完成三条 Google Vids 视频并上传 YouTube，回填链接、文章内交叉链接。
- [ ] 完成技术演示的 YouTube 发布设置并回填可访问链接。
- [ ] 将最终版本 commit/push 到私有 GitHub 仓库。
- [ ] 给课程工作人员私有仓库访问权限（需其 GitHub 用户名）。
- [ ] 由账号持有人轮换之前在聊天中暴露的 OpenAI key。

下面保留原始操作指南；以顶部状态及实际产物为准。

---

# 原始操作指南

流水线能做的都已做完：第一次 live run 已批准并打包在
`runs/20261013T213636Z-podcasts-expanded/package/`。下面每一项都需要本人账号或另一天的时间，
按顺序做即可。做完可以删掉这个文件，或留着也不影响评分。

## 1. 发布三篇 Substack 文章（约 15 分钟）
- [ ] 用浏览器打开 `package/01-article.html`，Cmd-A 全选、复制，粘贴到 Substack 新帖子；标题用第一行；
      如果 Substack 重复了 H1 就删掉一个；保留文末 *As of 2026-10-13* 行和 Sources 列表。
- [ ] 同样处理 `02-article.html`、`03-article.html`。
- [ ] 每篇设为免费、公开，发布后复制 URL。

## 2. 生成三条视频（Google Vids 或 HeyGen）
- [ ] 手动：按 `package/NN-video-script.md` 逐幕制作——`Visual` 是画面说明，`On-screen text` 是字幕/标题，
      `Narration` 是口播（删掉 `[n]` 标记，不要读出来）。目标 3–5 分钟。
- [ ] 或用 HeyGen API（需要 HeyGen 账号的 API key，只放环境变量）：
      ```bash
      export HEYGEN_API_KEY=...            # 不要写进任何文件
      .venv/bin/python tools/heygen_render.py runs/20261013T213636Z-podcasts-expanded --list-avatars
      .venv/bin/python tools/heygen_render.py runs/20261013T213636Z-podcasts-expanded --list-voices
      .venv/bin/python tools/heygen_render.py runs/20261013T213636Z-podcasts-expanded --avatar <AVATAR_ID> --voice <VOICE_ID>
      ```
      产物在 `package/videos/NN.mp4`（已被 .gitignore 忽略）。脚本未用真实 key 测试过，若 API 报错会原样打印。

## 3. 上传 YouTube（公开或不公开均可）
- [ ] 手动：标题用脚本第一行；描述粘贴 `package/NN-youtube-description.txt`，把 `[substack link to add]`
      换成对应文章 URL。
- [ ] 或用 API：按 `tools/youtube_upload.py` 开头说明建一次 Google OAuth 客户端（约 10 分钟），然后
      ```bash
      YOUTUBE_CLIENT_SECRET=/path/client_secret.json .venv/bin/python tools/youtube_upload.py runs/20261013T213636Z-podcasts-expanded --privacy unlisted
      ```

## 4. 回填链接并刷新摘要
- [ ] 每篇执行（会自动重跑 `bash run.sh --package`，草稿不会被改动）：
      ```bash
      .venv/bin/python tools/record_links.py runs/20261013T213636Z-podcasts-expanded 01 --substack <URL> --youtube <URL>
      ```
      或直接编辑 `package/publication_links.json` 后运行 `bash run.sh --package runs/20261013T213636Z-podcasts-expanded`。
- [ ] 回到 Substack 每篇文章里加上对应视频链接。
- [ ] 把三篇标题和六个链接填进 `SUBMISSION.md` 的 "Published Series" 表。
- [ ] 请同学/用无痕窗口确认链接可打开。

## 5. 第二次 live run（必须是另一天）
- [ ] 终端运行：`bash run.sh`（约 20–40 分钟；已入库的材料全部复用，只转写新集数；政策 v2 已生效）。
- [ ] 看 `runs/<新RUN_ID>/summary.json` 的 `status`、`counts.new/changed/unchanged`、`review.passed`。
- [ ] 复核 `decisions.jsonl`、`articles/`、`video_scripts/`；如需修改直接改文件，然后
      `bash review/check_content.sh runs/<新RUN_ID> > runs/<新RUN_ID>/review.json`。
- [ ] 写 `runs/<新RUN_ID>/approval.json`（`review_id` 取 review.json 当前值，`decision: "approve"`，
      `reviewer`、`reviewed_at`、`notes`），再 `bash run.sh --package runs/<新RUN_ID>`。
- [ ] 填 `SUBMISSION.md` 运行表的 "Second live run" 一行，并在 "What changed between runs" 补两句：
      新发现/变化了什么、编辑选择或综合因此有何变化（没有新材料也要如实写）。
- [ ] `runs/README.md` 加一行。第二次 run 不要求再发布一整套，但如果有新稿可作为后续期。

## 6. 技术演示视频（4–6 分钟，单独录制）
- [ ] 建议镜头：`SUBMISSION.md` 架构图 → `run.sh` 与两个 workflow → 终端跑
      `bash tools/trace_claim.sh runs/20261013T213636Z-podcasts-expanded 03-c9`（claim 到播客时间戳）
      → 第二次 run 的 `changes.jsonl`（unchanged/new）→ `runs/20261014T005920Z-simulated-failure/summary.json`
      （coverage_complete=false）→ `runs/20261013T230227Z-policy-v2/decisions_diff.md`（政策修订效果）
      → `corrections.jsonl` 里 Naresh Jain 的归属修正 → 一个架构取舍（SQLite 索引 + 内容寻址资产文件）。
- [ ] 链接填进 `SUBMISSION.md` 的 "Separate technical demonstration video"。

## 7. 提交到 GitHub
- [ ] 文件已 `git add` 暂存（7 MB，无音频、无密钥）。执行：
      ```bash
      git commit -m "PS4 intelligence pipeline: Harness Notes"
      git remote add origin <你的仓库 URL> && git push -u origin main
      ```
- [ ] 把仓库链接填进 `SUBMISSION.md` 顶部。第二次 run 之后再 commit/push 一次。

## 8. 安全与环境
- [ ] 轮换曾在聊天里贴出的 OpenAI key（它没有写入任何文件）。
- [ ] 磁盘约 4 GB 余量；第二次 run 若空间紧张，用 `RETAIN_MEDIA=0 bash run.sh`（转写完即删音频）。
