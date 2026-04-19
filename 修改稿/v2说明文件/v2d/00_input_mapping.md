# v2d Input Mapping

## Token

- `v2d`

## 本轮实际采用的审稿/修改建议文件

- 主审稿报告：`C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\修改稿\v2修改建议\V2_retained_manuscript_review_report.docx`
- 重复副本一：`C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\修改稿\v2初始版\v2c_recheck_top_journal_review.docx`
- 重复副本二：`C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\修改稿\v2修改建议\v2c修改建议\v2c_recheck_top_journal_review.docx`

说明：

- 读取正文内容后确认，`v2c_recheck_top_journal_review.docx` 两处副本都是“复核/审稿报告”，不是被修订正文。
- `V2_retained_manuscript_review_report.docx` 明确写明评估对象是 `修改稿/v2修改稿留底` 目录下的留底版本，而不是 `修改稿/v2初始版/`。

## 被审 v2c 稿件识别逻辑

### 搜索顺序与结果

1. `修改稿/v2初始版/`
   - 检测到 `v2c_recheck_top_journal_review.docx`
   - 读取正文后确认其为审稿/复核报告，不是被审正文稿
2. `修改稿/v2修改稿留底/v2c/`
   - 检测到 `PPP论文_完整论文初稿_公共管理风格_顶刊冲刺整合稿_v2c_本轮修订版_20260418_对象保留版.docx`
   - 与审稿报告中“评估对象为 v2修改稿留底 目录下的论文留底版本”一致
3. `修改稿/v2说明文件/v2c/`
   - 检测到 `PPP论文_完整论文初稿_公共管理风格_顶刊冲刺整合稿_v2c_本轮修订版_20260418.md`
   - 作为与被审对象同步的可编辑 Markdown 底稿
4. 其他 v2c 相关文件
   - 审稿报告提到 `v2c.zip`、`revised_paper_v2c.docx`、`revision_checklist_v2c.md`、`log_ratio_robustness_v2c.csv`
   - 当前仓库未恢复到这些同名文件，但 `v2说明文件/v2c/` 中已有与之同功能的现行资产

### 识别结论

- 被审的精确 v2c 源稿件：
  - `C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\修改稿\v2修改稿留底\v2c\PPP论文_完整论文初稿_公共管理风格_顶刊冲刺整合稿_v2c_本轮修订版_20260418_对象保留版.docx`
- 本轮 forward-apply 的可编辑底稿：
  - `C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\修改稿\v2说明文件\v2c\PPP论文_完整论文初稿_公共管理风格_顶刊冲刺整合稿_v2c_本轮修订版_20260418.md`

原因：

- 被审对象必须与审稿报告的显式说明一致，因此精确匹配到 `v2修改稿留底/v2c/` 的对象保留版 docx。
- 实际修订需要结构化文本编辑，因此先将修改前移到 `v2d` 工作目录中的 md，再回填到新的对象保留版 docx。

## 本轮读取的 source of truth

- `C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\AGENTS.md`
- `C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\00_环境说明与索引\01_工作区归类说明_20260419.md`
- `C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\00_环境说明与索引\02_文件定位清单_20260419.md`
- `C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\00_环境说明与索引\03_Git与运行环境同步说明_20260419.md`
- `C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\修改稿\README_版本留底与Git同步规则.md`
- `C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\修改稿\索引\修改稿索引总览.md`
- `C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\修改稿\索引\v2修改稿索引.md`
- `C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\ppp论文数据\PPP_v3结果层状态表_20260413_1345.xlsx`
- `C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\ppp论文数据\PPP_变量与模型最终采用口径表_20260413_1345.xlsx`
- `C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\数据总表（一切数据基础）.xlsx`
- `C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\ppp论文数据\参考文献\`
- `C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\PPP_empirical_reinforcement_bundle_20260416_unified_v3\04_manuscript_integration\`

## 本轮 authority hierarchy

1. `AGENTS.md`
2. `00_环境说明与索引/` 下的环境与同步规则
3. `V2_retained_manuscript_review_report.docx`
4. 被审 v2c 对象保留版与其同步 md 底稿
5. `PPP_v3结果层状态表_20260413_1345.xlsx`
6. `PPP_变量与模型最终采用口径表_20260413_1345.xlsx`
7. `数据总表（一切数据基础）.xlsx`
8. `PPP_empirical_reinforcement_bundle_20260416_unified_v3/04_manuscript_integration/` 下的正式整合稿、caption notes 与防守补充材料
9. `ppp论文数据/参考文献/` 中可核实的本地文献 PDF

## v2d 本轮输出底稿

- 工作中的修订 md：
  - `C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\修改稿\v2说明文件\v2d\PPP论文_完整论文初稿_公共管理风格_顶刊冲刺整合稿_v2d_0419_1528.md`
- 对象保留回填目标：
  - `C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\修改稿\v2说明文件\v2d\PPP论文_完整论文初稿_公共管理风格_顶刊冲刺整合稿_v2d_0419_1528_对象保留版.docx`
