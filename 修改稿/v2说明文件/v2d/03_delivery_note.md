# v2d Delivery Note

交付日期：2026-04-19

## 1. 本轮使用的审稿/建议文件

- 主建议文件：
  - `修改稿/v2修改建议/V2_retained_manuscript_review_report.docx`
- 复核副本：
  - `修改稿/v2初始版/v2c_recheck_top_journal_review.docx`
  - `修改稿/v2修改建议/v2c修改建议/v2c_recheck_top_journal_review.docx`

## 2. 本轮识别并修订的源稿

- 被审 `v2c` 正式对象稿：
  - `修改稿/v2修改稿留底/v2c/PPP论文_完整论文初稿_公共管理风格_顶刊冲刺整合稿_v2c_本轮修订版_20260418_对象保留版.docx`
- forward-apply 的文本底稿：
  - `修改稿/v2说明文件/v2c/PPP论文_完整论文初稿_公共管理风格_顶刊冲刺整合稿_v2c_本轮修订版_20260418.md`

说明：
- 本轮没有把 `v2c_recheck_top_journal_review.docx` 误当成正文稿。
- 处理方式是：
  - 先在 `v2c md` 的可编辑文本底稿上完成结构化修订
  - 再回填到被审 `v2c` 对象保留版 `docx`

## 3. 已采纳的核心修改

- 标题与摘要进一步收口为“条件关联证据”，不再保留过强因果口径。
- 第4.3节补足 `treat_share` 的公式、变量角色和样本流转链条：
  - `1472 → 1307 → 288 → 266 → 262`
  - 外加 `10000` 个项目级扩展样本
- 第4.4节明确 `β` 的平均条件关联含义，并将 `did_any` / `did_intensity` 压回替代口径与诊断层。
- 第5.4节改写为“政策文本证据线索与阶段性传导”，避免把同源文本工程写成独立强机制识别。
- 第5.6节把 trend-adjusted DID 与 wild cluster bootstrap 纳入主防守叙述，并写入关键数值。
- 结论同步收口：
  - `exec_share` / `proc_share` 仍是主结果
  - `ppp_quality_zindex` 继续只作边界性结果
  - 机器学习继续只作治理辅助识别
- 新增附录C/D/E，分别处理：
  - 文本池与样本流转一致性
  - 主识别防守结果摘要
  - 处理变量与文本证据线索的来源边界
- 参考文献中补齐肖永慧（2025）条目的卷期页码与 DOI。

## 4. 未采纳或降格处理的建议

- 未采纳“165 = 全量政策文本池”的 manuscript-facing 写法。
  - 原因：当前仓库现行正式文件不能支持该口径。
  - 替代处理：统一维持 `1472 → 1307 → 288 → 266 → 262` 的正式链条，并在附录C说明为何不采纳。
- 未把 stack DID、cohort ATT、PSM-DID、DML、IV 候选抬升为主识别或第二主模型。
  - 原因：与 `AGENTS.md` 及正式识别层级冲突。
- 未把 A/B/C/D 结果继续写成“强机制检验”。
  - 原因：与 `treat_share` 同源，独立性不足。

## 5. 数据与分析处理状态

- 本轮未改动原始 `.xlsx` 工作簿。
- 本轮未新增全套回归重跑。
- 本轮复用并核验了此前已落地的 fresh re-estimate：
  - `appendix_B_log_ratio_reestimate_20260418.csv`
- 本轮重新对照官方结果表同步正文与附录中的防守性数值。

## 6. 本轮输出清单

- 工作输出目录：
  - `修改稿/v2说明文件/v2d/`
- 主文稿：
  - `PPP论文_完整论文初稿_公共管理风格_顶刊冲刺整合稿_v2d_0419_1528.md`
  - `PPP论文_完整论文初稿_公共管理风格_顶刊冲刺整合稿_v2d_0419_1528_对象保留版.docx`
- 说明文件：
  - `00_input_mapping.md`
  - `01_revision_tasklist.md`
  - `02_verification_report.md`
  - `03_delivery_note.md`
- 附录侧车资产：
  - `appendix_A_*`
  - `appendix_B_*`
  - `appendix_C_sample_flow_0419_1528.csv`
  - `appendix_D_defensive_inference_summary_0419_1528.csv`
  - `appendix_E_source_boundary_0419_1528.md`
- 对象保留回填脚本与日志：
  - `generate_v2d_object_preserving_docx_0419_1528.py`
  - `docx_generation_log_0419_1528.md`

## 7. 剩余风险与人工 follow-up

- 若后续需要把附录A升级为完整城市级复现包，仍需补齐城市级处理名单与原始阈值底表。
- 若环境恢复可联网，建议再次执行仓库同步和远端 push 复核。
- 若作者后续拿回确切的“165”审计窗口原表，应以独立名称单列，不能覆盖当前正式全文政策文本池口径。
