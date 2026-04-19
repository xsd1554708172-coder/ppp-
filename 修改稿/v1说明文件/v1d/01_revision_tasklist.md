# v1d Revision Tasklist

## Revision Basis

- 主复审依据：
  - `v1c_top_journal_review_report.docx`
- 辅助顶刊化依据：
  - `V1 版本内容复审与顶刊化润色报告.docx`
- 正式结果与变量口径依据：
  - `PPP_v3结果层状态表_20260413_1345.xlsx`
  - `PPP_变量与模型最终采用口径表_20260413_1345.xlsx`
  - 正式主面板 / 文本变量表 / `robustness_defense_summary.xlsx`

## Adopted This Round

### 1. 数据与结果透明度补强

- 状态：`Adopted`
- 具体动作：
  - 用正式主面板 `sample_screen`、`missing_from_288_to_266`、`dropped_from_266_to_262` 三个 sheet 重写 4.1 样本流说明。
  - 在 4.3 中补写 `treat_share`、`exec_share`、`proc_share` 的取值区间和样本均值。
  - 在 4.2 中补写文档级 `1307` -> 省年 `288` -> 主面板 `266` -> 正式估计 `262` 的可追溯链条。

### 2. 文本变量工程透明度补强

- 状态：`Adopted`
- 具体动作：
  - 根据 `build_ppp_text_variables_v2.py` 与两份 README，将 A/B/C/D 变量写成“文档提取 -> 省年聚合 -> 正式并表 -> 正文使用”的变量工程链条。
  - 明确当前材料足以支撑可追溯性与构造透明度，但不足以支撑新的独立外部效度强断言。

### 3. 主识别边界继续收紧

- 状态：`Adopted`
- 具体动作：
  - 继续保持 `treat_share` 多期 DID / TWFE 为唯一主识别。
  - 用 `robustness_defense_summary.xlsx` 和 `table_figure_caption_notes.md` 固定 5.6 的防守型口径。
  - 将 `ppp_quality_zindex` 继续压在 boundary result only 的位置。

### 4. 正文残留口径清理

- 状态：`Adopted`
- 具体动作：
  - 删除正文里的 `V3主面板`、`第5部分正式估计` 等工程残留式表达。
  - 将“净效应”改为更克制的“平均结构关联”表述。

### 5. 项目级机器学习扩展再压缩

- 状态：`Adopted`
- 具体动作：
  - 将 5.7 收束到核心识别力指标与治理辅助边界。
  - 明确参数调优、模型比较和特征贡献不进入正文主论证。

### 6. 结论与政策建议再压缩

- 状态：`Adopted`
- 具体动作：
  - 将学术补位压缩成 3 个高层贡献点。
  - 将政策建议压缩为 3 条、并按部门职责与证据边界收束。

## Partially Adopted

### 7. 文献综述重构

- 状态：`Partially adopted`
- 本轮处理：
  - 沿用四组文献结构，不再把文献综述写成方法展示。
  - 继续保留已核校程度较高的正式参考材料。
- 未完全展开的部分：
  - 报告建议的 `30—40` 条 fully checked bibliography，本轮没有直接落满。
- 原因：
  - 当前 `参考文献` 目录下部分文献条目仍缺完整、可核校的卷期页码或作者信息，不能编造。

## Not Adopted This Round

### 8. 新增组时 ATT / 连续处理 DID / 随机化推断重跑

- 状态：`Not adopted`
- 原因：
  - 当前正式口径表没有把这些 fresh 结果实体纳入 manuscript-facing 正式入口。
  - 在没有 fresh、正式审计结果的前提下，不能把它们补写成新的主识别或第二主防守。

### 9. 新增独立文本变量效度审计包

- 状态：`Not adopted`
- 原因：
  - 当前项目已有变量构造链条、README 与 doc-level / province-year outputs，可支撑透明度补强；
  - 但没有新的、正式审计完成的人工一致性统计、替代词典结果或主题稳定性结果可直接回填。

### 10. 表图重作 / 新图新增

- 状态：`Not adopted`
- 原因：
  - 当前 Figure 8A / 8B / 9 与 Table 8 的正文口径已在正式 notes 中固定。
  - 本轮没有数据修正或回归重跑，不宜为追求形式而重画。

## Rerun Decision

- `data correction needed`：`No`
- `raw workbook edit needed`：`No`
- `script rerun needed`：`No`
- 说明：
  - 本轮是基于正式结果实体与变量构造链条的 manuscript-facing 修订；
  - 没有发现必须改 raw workbook 或重新估计才能维持一致性的冲突。
