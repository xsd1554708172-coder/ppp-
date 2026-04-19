# v2d Verification Report

验证日期：2026-04-19

## 1. 输入映射核验

- 审稿/修改建议文件采用：
  - `修改稿/v2修改建议/V2_retained_manuscript_review_report.docx`
  - 并复核其重复副本：`修改稿/v2初始版/v2c_recheck_top_journal_review.docx`、`修改稿/v2修改建议/v2c修改建议/v2c_recheck_top_journal_review.docx`
- 被审 v2c 源稿识别为：
  - `修改稿/v2修改稿留底/v2c/PPP论文_完整论文初稿_公共管理风格_顶刊冲刺整合稿_v2c_本轮修订版_20260418_对象保留版.docx`
- 本轮结构化文本修订底稿采用：
  - `修改稿/v2说明文件/v2c/PPP论文_完整论文初稿_公共管理风格_顶刊冲刺整合稿_v2c_本轮修订版_20260418.md`
- 判定：`PASS`

## 2. source-of-truth 核验

- 已对照 `PPP_v3结果层状态表_20260413_1345.xlsx` 核验表4、trend-adjusted DID、wild cluster bootstrap 的 manuscript-facing 数值。
- 已对照 `PPP_变量与模型最终采用口径表_20260413_1345.xlsx` 核验 `treat_share` / `did_intensity` / `did_any` 的变量角色与主识别层级。
- 已对照 `数据总表（一切数据基础）.xlsx` 核验政策文本全文池的 1472 口径。
- 已对照 `ppp论文数据/参考文献/` 中可核实 PDF，补齐肖永慧（2025）条目的卷期页码与 DOI。
- 判定：`PASS`

## 3. 文稿正文核验

- 标题已改为“政务服务数字化改革与PPP项目推进结构重组”，副标题已收口为“基于政策文本量化与省级面板的条件关联证据”。
- 摘要已同步写入三层结果边界：
  - baseline：`exec_share = 0.3556`，`proc_share = -0.4023`
  - log-ratio：`3.1916`，`p = 0.0277`
  - defensive inference：trend-adjusted DID 与 wild cluster bootstrap 的关键 `p` 值
- 第4.3节已显式写入样本流转：
  - `1472 → 1307 → 288 → 266 → 262`
  - 并注明项目级扩展样本 `10000`
- 第4.4节已保持唯一主识别为 `treat_share` 多期 DID / TWFE，且将 `β` 明确为平均条件关联解释。
- 第5.4节已改写为“政策文本证据线索与阶段性传导”，未再将 A/B/C/D 结果写成独立强机制识别。
- 第5.6节已把 trend-adjusted DID 与 wild cluster bootstrap 写回正文主防守层。
- 结论已同步收口，不再夸大 `ppp_quality_zindex` 或 event study。
- 判定：`PASS`

## 4. 红线核验

- `treat_share` 多期 DID / TWFE 仍是唯一主识别：`PASS`
- 未把 trend-adjusted DID、leave-one-province-out、wild bootstrap、stack DID、cohort ATT、PSM-DID、DML、IV 候选写成主识别：`PASS`
- 未写“事件研究证明平行趋势成立”或同义强表述：`PASS`
- 未把 `ppp_quality_zindex` 抬升为主结论：`PASS`
- 机器学习仍定位于治理辅助识别扩展分析：`PASS`

## 5. 数值与附录一致性核验

- 正文 baseline 数值与官方结果表一致：
  - `exec_share = 0.3556`
  - `proc_share = -0.4023`
- 正文 defensive 数值与官方结果表一致：
  - trend-adjusted DID：`0.2263 / -0.3521 / -0.1699`
  - wild cluster bootstrap `p` 值：`0.0761 / 0.1221 / 0.2372`
- 附录B与侧车文件一致：
  - `appendix_B_log_ratio_reestimate_20260418.csv`
  - `appendix_B_log_ratio_note_20260418.md`
- 附录C/D/E已落地并在正文对象版中可检索：
  - `appendix_C_sample_flow_0419_1528.csv`
  - `appendix_D_defensive_inference_summary_0419_1528.csv`
  - `appendix_E_source_boundary_0419_1528.md`
- “165 = 全量政策文本池”未被采纳，并在附录C中明确说明原因：`PASS`

## 6. 对象保留版 docx 核验

- 输出文件：
  - `修改稿/v2说明文件/v2d/PPP论文_完整论文初稿_公共管理风格_顶刊冲刺整合稿_v2d_0419_1528_对象保留版.docx`
- 生成方式：
  - 以被审 `v2c` 对象保留版 `docx` 为源包，只替换 `word/document.xml`
- package 级对象保留核验：
  - source media count：`13`
  - output media count：`13`
  - charts：`0 → 0`
  - embeddings：`0 → 0`
- 内容核验：
  - 新标题、新摘要、`1472` 样本流转、`3.1916`、附录C/D/E、肖永慧（2025）DOI 均可检索
  - 旧尾部附录 `附录A 文本分析诊断与样本补充` 已移除
  - `图B3 不同阈值下的成本收益权衡` 未残留在 manuscript-facing 文稿尾部
- 判定：`PASS`

## 7. fresh rerun / data edit 核验

- 本轮未新增修改原始工作簿或官方 `.xlsx`。
- 本轮未新增全套回归重跑。
- 本轮复用了 2026-04-18 已落地的 fresh log-ratio re-estimate 资产，并重新对照官方结果层状态表核验 manuscript-facing 数值。
- 结论：`PASS`

## 8. 仍存边界

- 城市级处理名单、原始阈值底表未在当前仓库显式落地，因此附录A仍是 province-year 重构层面的复核资产，而不是完整城市级复现包。
- 该边界已在正文、附录A和 delivery note 中同步写明，不构成本轮 `v2d` 交付阻断。

## 9. 总体判定

`v2d` 的 `md`、对象保留版 `docx`、说明文件与附录侧车资产已经完成一致性核验，可以进入归档、打包与 Git 收尾阶段。
