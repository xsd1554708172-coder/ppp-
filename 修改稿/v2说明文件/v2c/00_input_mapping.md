# v2c Input Mapping

## Token

- `v2c`

## 自动识别结果

- `修改稿\v2` 检测到的 token-local 文件：
  - `C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\修改稿\v2\v2c_recheck_top_journal_review.docx`
- `修改稿\v2修改建议` 检测结果：
  - 无文件
- `修改稿\v2说明文件\v2c`：
  - 本轮输出目录

## 本轮实际读取文件

### token-local / 指定目录

- `C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\修改稿\v2\v2c_recheck_top_journal_review.docx`

### 正式口径与总控文件

- `C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\AGENTS.md`
- `C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\记忆部分或工作交接\2026-04-17_投稿目标修正记忆_顶刊冲刺.txt`
- `C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\ppp论文数据\PPP_v3结果层状态表_20260413_1345.xlsx`
- `C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\ppp论文数据\PPP_变量与模型最终采用口径表_20260413_1345.xlsx`

### 正式整合稿与对象保留稿

- `C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\PPP_empirical_reinforcement_bundle_20260416_unified_v3\04_manuscript_integration\PPP论文_完整论文初稿_公共管理风格_顶刊冲刺整合稿_20260418_投稿版.md`
- `C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\PPP论文_完整论文初稿_公共管理风格_顶刊冲刺整合稿_20260418_对象保留投稿版.docx`

### 可复核补充资产

- `C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\PPP_empirical_reinforcement_bundle_20260416_unified_v3\04_manuscript_integration\notes\table_figure_caption_notes.md`
- `C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\PPP_empirical_reinforcement_bundle_20260416_unified_v3\04_manuscript_integration\notes\methods_supplement_patch_20260417.md`
- `C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\PPP_empirical_reinforcement_bundle_20260416_unified_v3\04_manuscript_integration\notes\EXACT_REPLACEMENT_PATCH_20260417.md`
- `C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\ppp论文数据\01_第3到第8部分_最终修正版\第5部分_核心实证识别\（5.1）识别框架、并表与模型设定\PPP_第5部分_5.1并表与模型设定_V2_四级十二类_实际执行版.xlsx`
- `C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\ppp论文数据\01_第3到第8部分_最终修正版\第5部分_核心实证识别\（5.1）识别框架、并表与模型设定\PPP_3.6_model_ready_panel_v3_统一口径_方案2_实际执行版_20260413_1048.csv`
- `C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\ppp论文数据\01_第3到第8部分_最终修正版\第5部分_核心实证识别\（5.3）基准多期DID_TWFE正式回归\PPP_第5部分_5.3正式回归结果长表_V3_重估版_20260413_1048.csv`

## fallback 是否发生

- `是`

### fallback 原因

- 指定 `v2` 目录中没有 `v2c` 原始正文稿件。
- 指定 `v2修改建议` 目录中没有任何可用建议文件。
- 审查报告点名的 `v2c.zip` 及其内部 `revised_paper_v2c.docx` / `revision_checklist_v2c.md` / `log_ratio_robustness_v2c.csv` 未能在仓库中恢复。

### fallback 执行方式

- 审查/建议来源 fallback 到 `v2c_recheck_top_journal_review.docx`。
- 正文编辑底稿 fallback 到 2026-04-18 正式整合稿 `md/docx`。
- 结果与变量口径 fallback 到正式状态表、变量口径表、5.1/5.3 工作簿与结果长表。

## 本轮 authority hierarchy

1. `AGENTS.md`
2. `2026-04-17_投稿目标修正记忆_顶刊冲刺.txt`
3. `v2c_recheck_top_journal_review.docx` 中可核实的审查意见
4. `PPP_v3结果层状态表_20260413_1345.xlsx`
5. `PPP_变量与模型最终采用口径表_20260413_1345.xlsx`
6. 2026-04-18 正式整合稿 `md/docx`
7. `table_figure_caption_notes.md`、`methods_supplement_patch_20260417.md`、`EXACT_REPLACEMENT_PATCH_20260417.md`
8. 5.1 并表说明、V3 正式主面板、5.3 正式结果长表
9. 参考文献目录中的可用材料

## 输出底稿

- Markdown：
  - `C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\修改稿\v2说明文件\v2c\PPP论文_完整论文初稿_公共管理风格_顶刊冲刺整合稿_v2c_本轮修订版_20260418.md`
- 对象保留版 DOCX：
  - `C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\修改稿\v2说明文件\v2c\PPP论文_完整论文初稿_公共管理风格_顶刊冲刺整合稿_v2c_本轮修订版_20260418_对象保留版.docx`
