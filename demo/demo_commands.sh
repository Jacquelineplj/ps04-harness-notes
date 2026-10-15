#!/usr/bin/env bash
# Harness Notes — 技术演示命令清单
# 顺序与 demo/technical_demo_script_v2.md 完全一致。全部只读，不修改任何文件。
#
# 录制时：把本文件开在记事本/编辑器里，从下面的 ── 标记处整块复制粘贴，
#         等输出出现，再念稿子里对应那一段。标记行是注释，连着复制也不会报错；
#         如果你的终端对 # 开头的行报错，就只复制命令本身。
# 预热时：bash demo/demo_commands.sh   按顺序把所有命令跑一遍。
#
# 第 0 步没有命令：编辑器打开 SUBMISSION.md，滚到 Architecture 的 mermaid 图。

# ↓↓ 下面这一行只在整体预热时起作用，复制单块时不需要 ↓↓
cd "$(dirname "${BASH_SOURCE[0]:-$0}")/.." 2>/dev/null || true

# ── 1.1  入口和组件
ls run.sh workflows/*.sh collectors/*.sh processing/*.sh data/store.sh \
   editorial/*.sh content/*.sh review/*.sh publishing/*.sh reporting/*.sh

# ── 1.2  入口和组件
sed -n '3,5p' run.sh

# ── 1.3  入口和组件
bash data/store.sh get feed:7e289d45dfc4cd8f | jq -r '"\(.kind)  \(.publisher_id)  \(.title)\nversion \(.version_id[0:12])  text \(.text_path)"'

# ── 2.1  一条论断追到已发布的文章
bash tools/trace_claim.sh runs/20261013T213636Z-podcasts-expanded 03-c9

# ── 3.1  第二次运行与一次真实变更
jq -r '.counts | "new=\(.new) changed=\(.changed) unchanged=\(.unchanged)"' runs/20261014T014037Z-second-live/summary.json
jq -r '.counts | "new=\(.new) changed=\(.changed) unchanged=\(.unchanged)"' runs/20261015T014725Z-ny-next-day-live/summary.json

# ── 3.2  第二次运行与一次真实变更
sqlite3 data/evidence/evidence.sqlite "select version_id, first_run_id from versions where item_id='feed:7e289d45dfc4cd8f'"

# ── 3.3  第二次运行与一次真实变更
diff data/assets/feed/d32c876482ebf166/{f7fb768c88d4,b4aca652c1f4}.txt | grep '^>' | fold -w 92 -s

# ── 4.1  一次真实故障和一次标注的失败
jq -r '.status + " :: " + .errors[0].message' runs/20261013T204414Z/logs/collect_sources-*.json

# ── 4.2  一次真实故障和一次标注的失败
jq '.coverage.collection.collectors, .coverage.coverage_complete' runs/20261014T005920Z-simulated-failure/summary.json

# ── 5.1  一处人工修正与一次政策修订
jq -r 'select(.reason|test("Naresh Jain")) | .before[0:55] + "  ->  " + .after[0:55]' runs/20261013T213636Z-podcasts-expanded/corrections.jsonl | head -3

# ── 5.2  一处人工修正与一次政策修订
head -5 runs/20261013T230227Z-policy-v2/decisions_diff.md

# ── 6.1  架构取舍与系统的终点
sed -n '/^SCHEMA = /,/^"""/p' data/store.py | head -20
ls -l data/assets/feed/d32c876482ebf166/

# ── 6.2  架构取舍与系统的终点
ls runs/20261013T213636Z-podcasts-expanded/package

# ── 可选一（时间有富余，插在 1.3 之后）：任一阶段的 receipt
jq -c '{stage,status,input_count,output_count,elapsed_seconds,cost_usd,cost_is_estimate}' runs/20261015T014725Z-ny-next-day-live/logs/select_items-*.json

# ── 可选二（时间有富余，插在 1.3 之后）：30 天窗口的排除记录
head -2 runs/20261015T014725Z-ny-next-day-live/exclusions.jsonl | jq -c '{item_id,reason,detail}'

