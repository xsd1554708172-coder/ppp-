# v2d Revision Tasklist

| 类别 | 审稿要求 | 本轮动作 | 状态 | 备注 |
|---|---|---|---|---|
| 识别映射 | 先分清审稿报告与被审正文 | 读取三份 `v2c_recheck...docx` / `V2_retained...docx`，明确被审对象是 `v2修改稿留底/v2c` 的对象保留版 | 已完成 | 见 `00_input_mapping.md` |
| 纯文字修订 | 标题与摘要进一步收口为“条件关联证据” | 将标题改为“政务服务数字化改革与PPP项目推进结构重组”，摘要同步写入 baseline / trend-adjusted / wild 边界 | 已完成 | 已同步到 md；后续回填 docx |
| 识别策略澄清 | 保持 `treat_share` 多期 DID / TWFE 为唯一主识别 | 重写 4.4，对 `β` 改写为平均条件关联；压低 `did_any`/`did_intensity` 为替代口径 | 已完成 | 未抬升任何替代模型 |
| 数据口径修正 | 公布 `treat_share` 公式与样本流转 | 在 4.3 明确公式，并补齐 `1472→1307→288→266→262` 与 `10000` 扩展样本口径 | 已完成 | 另落地 `appendix_C_sample_flow_0419_1528.csv` |
| 表图/附录调整 | 处理 Table 10 / “165” 口径冲突 | 不沿用 unsupported 的“全量文本池165”；在附录C显式说明为何不采纳 | 已完成 | 以正式源文件为准 |
| 份额型结果处理 | 补强 share outcome 的构成性处理 | 保留 baseline 表述，并明确 `log-ratio` 只作构成性补强 | 已完成 | 复用 `20260418` fresh re-estimate |
| 防守检验 | 把 trend-adjusted DID 与 wild cluster bootstrap 拉回主防守层 | 在 5.6 与结论中同步写入 `0.2263 / -0.3521 / 0.0761 / 0.1221` 等关键数值 | 已完成 | 另落地 `appendix_D_defensive_inference_summary_0419_1528.csv` |
| 机制边界 | 避免同源文本被写成独立强机制 | 将 5.4 改写为“政策文本证据线索与阶段性传导”，并新增附录E说明来源边界 | 已完成 | 明确不再使用“强机制检验”口径 |
| 参考文献修正 | 修复已能本地核实的参考文献元数据 | 更新肖永慧（2025）条目为本地 PDF 可核实的卷期页码与 DOI | 已完成 | 未编造其他元数据 |
| 不采纳项 | 不把 stack DID / cohort ATT / PSM-DID / DML / IV 抬升为主识别 | 仅保留为边界诊断或扩展说明 | 已完成 | 与 AGENTS 规则一致 |
| 不采纳项 | 不把 `ppp_quality_zindex` 抬升为主结论 | 保持为边际改善方向 | 已完成 | 与官方结果层状态表一致 |
| 不采纳项 | 不把“165”当成全量政策文本池写入正文 | 明确标记为 unsupported legacy label | 已完成 | 见附录C |
