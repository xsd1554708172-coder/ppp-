# 01_revision_tasklist

## A. 文字修订

1. 将标题副题收束为“基于政策文本量化与省级面板的条件关联证据”，避免把当前证据写成过强因果口径。
2. 重写摘要：保留正式主结果 `0.3556 / -0.4023`，加入 fresh log-ratio 补充结果 `3.1916, p = 0.0277`，同时明确 `ppp_quality_zindex` 不稳、event study 只作边界说明、ML 不进入主识别。
3. 重写第 4.1 节，统一样本链条为 `1472 -> 1307 -> 288 -> 266 -> 262`，并把 4 个兵团观察删样原因写清楚。
4. 重写第 4.3 节，显式给出 `treat_share` 定义、`did_intensity` / `did_any` 边界、处理时点集中于 2016/2017 的事实。
5. 重写第 4.4 节，将主识别口径明确收束为 `treat_share` 多期 DID / TWFE 下的平均条件关联，不把 event study 写成平行趋势“已成立”。
6. 在第 5.2 节中补写 log-ratio 结果，作为 share outcome 构成性约束的补充支持，而不是替代主模型。
7. 将第 5.4 节整体降格为“政策文本证据线索与阶段性传导”，不再把 A/B/C/D 与 `treat_share` 的关系写成独立强机制识别。
8. 收紧第 5.6 节与结论中的防守措辞，明确 trend-adjusted / leave-one-out / wild cluster 的层级只属于 defensive robustness / boundary diagnostics。
9. 在“研究透明度与复现说明”中加入 fresh rerun 与 blocker 说明。

## B. 结构修订

1. 保留全文唯一主识别：`treat_share` 多期 DID / TWFE。
2. 将原机制节改写为“政策文本证据线索与阶段性传导”，避免与主识别并列。
3. 在正文末尾新增附录 A-E：
   - 附录 A：处理变量与样本流转补充说明
   - 附录 B：对数比率补充估计说明
   - 附录 C：文本池与样本流转一致性说明
   - 附录 D：主识别防守结果摘要
   - 附录 E：处理变量与文本证据线索的来源边界
4. 将 rerun 结果、删样说明、变量口径说明从“口头解释”落到可打开的附件文件。

## C. 文献修订

1. 本轮未新增未经核实的文献元数据。
2. 保留 v1d 已有文献体系；主报告的批评重点在经验识别与复现闭环，而非新增文献缺口，因此本轮不编造卷期页码或未核实元数据。
3. 仅在正文表述中收紧“文本方法价值”“机器学习位置”“公共管理补位”的表述强度。

## D. 表图 / 附录 / 结果资产修订

1. 新增 `appendix_A_treat_share_reconstruction_20260419.csv`
2. 新增 `appendix_A_province_treatment_timing_20260419.csv`
3. 新增 `appendix_A_sample_exclusions_20260419.csv`
4. 新增 `appendix_A_treat_share_definition_tables_20260419.md`
5. 新增 `appendix_B_log_ratio_reestimate_20260419.csv`
6. 新增 `appendix_B_log_ratio_note_20260419.md`
7. 新增 `appendix_C_sample_flow_20260419.csv`
8. 新增 `appendix_C_sample_flow_note_20260419.md`
9. 新增 `appendix_D_defensive_summary_20260419.md`
10. 新增 `appendix_E_source_boundary_20260419.md`
11. 新增 `fresh_rerun_main_results_20260419.csv`
12. 新增 `fresh_rerun_vs_official_20260419.csv`
13. 新增 `fresh_rerun_summary_20260419.md`

## E. 数据口径修订

1. 将 v1d 中仍偏“叙述式”的样本口径，改写成可核对的正式链条：
   - 全文池：1472
   - DID 文本文档：1307
   - province-year 平衡窗口：288
   - V3 面板观测：266
   - 5.3 正式估计样本：262
2. 明确 4 个删样观察全部来自新疆生产建设兵团，且因为 8 个正式基准控制变量缺失未进入基准估计。
3. 明确本轮正式基准控制变量只使用 8 个控制项，而不再含混叠加旧口径。
4. 明确 treat_share 是连续暴露强度而非单次处理哑变量；`did_any` 和 `did_intensity` 只作为替代口径 / 诊断口径。

## F. 本轮实际 rerun 项

1. 基准 `treat_share` DID/TWFE fresh rerun：**已执行，且与官方 5.3 长表在机器精度上对齐**。
2. 执行/采购对数比率补充估计 fresh rerun：**已执行**。
3. 样本流转 fresh reconstruction：**已执行**。
4. province-year 层处理变量与处理时点表 fresh reconstruction：**已执行**。
5. trend-adjusted DID 零依赖手工 rerun：**已执行，但仅作为 diagnostic，不覆盖正文官方值**。

## G. 未采纳项及理由

1. **不把 trend-adjusted DID / stack DID / cohort ATT / PSM-DID / DML / IV candidate / ML 扩展写成主识别或第二主模型**。
   - 理由：违反项目主识别 hierarchy。
2. **不把 event study 写成“证明平行趋势成立”**。
   - 理由：主报告明确指出前趋势风险仍需保留。
3. **不把 `ppp_quality_zindex` 写成稳健主结论**。
   - 理由：正式结果与 fresh rerun 都不支持。
4. **不把 A/B/C/D 与 treat_share 的关系写成独立强机制识别**。
   - 理由：同源于政策文本工程，独立性不足。
5. **不直接修改原始 `.xlsx` 工作簿**。
   - 理由：本轮可以通过脚本与派生结果重构完成，不需要直接硬改原始数据。
6. **不声称已完成 city-level treatment registry 全复现**。
   - 理由：仓库缺少可直接审计的城市级处理名单与原始 threshold 表。
7. **不声称已完成 wild cluster bootstrap fresh rerun**。
   - 理由：当前环境缺少完整一键运行链与依赖环境，只保留官方已落地数值并写明 blocker。
