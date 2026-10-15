#!/usr/bin/env bash
# Harness Notes — 技术演示命令清单
# 顺序与 demo/technical_demo_script_v2.md 一致。全部只读，不修改任何文件。
#
# 录制时：从 ── 标记处整块复制粘贴，等输出出现再念稿子里对应那段。
#         标记行是注释，连着复制也不会报错（已在交互式 zsh 验证）。
# 预热时：bash demo/demo_commands.sh
#
# 第 0 步没有命令：编辑器打开 SUBMISSION.md，滚到 Architecture 的 mermaid 图。
# 第 2 步第二半没有命令：浏览器打开已发布的第三篇文章，搜 16,000 和 30:48。

# ↓ 这行只在整体预热时起作用，复制单块时不需要
cd "$(dirname "${BASH_SOURCE[0]:-$0}")/.." 2>/dev/null || true

# ── 第 1 步  入口
ls run.sh workflows/*.sh collectors/*.sh processing/*.sh data/store.sh \
   editorial/*.sh content/*.sh review/*.sh publishing/*.sh reporting/*.sh
sed -n '3,5p' run.sh

# ── 2.1  一条论断追回到源头
bash tools/trace_claim.sh runs/20261013T213636Z-podcasts-expanded 03-c9

# ── 3.1  跑第二次会发生什么
jq -r '.counts | "new=\(.new) changed=\(.changed) unchanged=\(.unchanged)"' runs/20261014T014037Z-second-live/summary.json
jq -r '.counts | "new=\(.new) changed=\(.changed) unchanged=\(.unchanged)"' runs/20261015T014725Z-ny-next-day-live/summary.json

# ── 3.2  跑第二次会发生什么
sqlite3 data/evidence/evidence.sqlite "select version_id, first_run_id from versions where item_id='feed:7e289d45dfc4cd8f'"

# ── 3.3  跑第二次会发生什么
diff data/assets/feed/d32c876482ebf166/{f7fb768c88d4,b4aca652c1f4}.txt | grep '^>' | fold -w 92 -s

# ── 第 4 步  出错的时候
jq -r '.status + " :: " + .errors[0].message' runs/20261013T204414Z/logs/collect_sources-*.json

# ── 第 5 步  我改了什么，政策又改了什么
jq -r 'select(.reason|test("Naresh Jain")) | .before[0:55] + "  ->  " + .after[0:55]' runs/20261013T213636Z-podcasts-expanded/corrections.jsonl | head -3
head -5 runs/20261013T230227Z-policy-v2/decisions_diff.md

# ── 6.1  我会为之辩护的取舍
ls -l data/assets/feed/d32c876482ebf166/

# ── 6.2  我会为之辩护的取舍
ls runs/20261013T213636Z-podcasts-expanded/package

# ══ 以下为可选补充，正片不用 ══

# ── 可选一：标注过的模拟采集失败（插在第 4 步之后）
jq '.coverage.collection.collectors, .coverage.coverage_complete' runs/20261014T005920Z-simulated-failure/summary.json

# ── 可选二：任一阶段的 receipt（插在第 1 步之后）
jq -c '{stage,status,input_count,output_count,elapsed_seconds,cost_usd,cost_is_estimate}' runs/20261015T014725Z-ny-next-day-live/logs/select_items-*.json

# ── 可选三：30 天窗口的排除记录（插在第 1 步之后）
head -2 runs/20261015T014725Z-ny-next-day-live/exclusions.jsonl | jq -c '{item_id,reason,detail}'

