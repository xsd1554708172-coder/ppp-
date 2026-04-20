# v2e Delivery Note

交付日期：2026-04-20

> 本轮交付是 `v2e` 顶刊冲刺执行包。人工确认后已完成可运行模块的 full rerun；未填充的 registry/机制/文本审计模板和未找到脚本的 log-ratio 仍为“未重跑，不得当作结果”。

## 1. 本轮完成内容

- 成功读取本地 `修改稿/v2修改建议/v2d修改建议/v2d_DID_冲刺修订报告_可下载版.docx`。
- 使用 Python 标准库抽取 `docx` 正文，生成可 diff 的 extracted markdown。
- 根据报告将 `v2d → v2e` 任务拆成 P0/P1/P2。
- 生成正文 patch，但未覆盖主文稿。
- 生成 empirical rerun checklist，并在人工确认后运行 baseline / trend-adjusted DID / leave-one-province-out / wild / robustness summary。
- 生成 DID 文献嵌入 patch；已对 14 篇 DID PDF 做本地元数据提取，但卷期页码仍待正式核验。
- 对 empirical reinforcement bundle 的关键脚本执行了 `py_compile` 语法检查；随后安装必要运行时依赖并执行 full rerun，状态见 `rerun_logs/rerun_status_summary.md`。

## 2. 可直接提交的文件

- `修改稿/v2修改建议/v2d修改建议/_codex_extracts/v2d_DID_冲刺修订报告_extracted.md`
- `修改稿/v2修改建议/v2e修改建议/00_input_mapping.md`
- `修改稿/v2修改建议/v2e修改建议/01_revision_tasklist.md`
- `修改稿/v2修改建议/v2e修改建议/02_verification_report.md`
- `修改稿/v2修改建议/v2e修改建议/03_delivery_note.md`
- `修改稿/v2修改建议/v2e修改建议/v2e_DID_冲刺修订执行计划.md`
- `修改稿/v2修改建议/v2e修改建议/v2e_manuscript_patch.md`
- `修改稿/v2修改建议/v2e修改建议/v2e_empirical_rerun_checklist.md`
- `修改稿/v2修改建议/v2e修改建议/v2e_literature_integration_patch.md`

## 3. 不能视为最终实证结果的内容

- `v2e_empirical_rerun_checklist.md` 中尚未执行的 registry / log-ratio / 独立机制 / 文本效度审计输出。
- `v2e_manuscript_patch.md` 中关于未来 fractional / compositional robustness 的段落。
- `v2e_DID_冲刺修订执行计划.md` 中关于独立机制变量和文本效度审计的设计。
- DID 文献 patch 中尚未逐篇核实的参考文献卷期页码。

## 4. 未修改的高风险文件

- 未修改 `v2d_DID_冲刺修订报告_可下载版.docx`。
- 未修改任何 v2d 主文稿 `.docx`。
- 未修改 `数据总表（一切数据基础）.xlsx`。
- 未修改 `ppp论文数据/*.xlsx`。
- 未修改 `.env`、密钥、生产配置。
- 未 commit，未 push。

## 5. 下一步建议

建议下一步人工处理：

1. 提供或确认城市处理名单来源；当前只能保留空 registry 模板。
2. 提供或确认处理阈值底表；当前只能保留阈值审计模板。
3. 核定 `treat_share` 是否接受等权城市计数作为正式审计口径，或改用人口/项目数/投资额权重。
4. 对 14 篇 DID PDF 逐篇核验正式参考文献元数据（作者、题名、期刊、年份、卷期页码、DOI）。
5. 决定是否把本轮 rerun 快照中的谨慎段落 forward-apply 到 v2e 正文 `.docx`。

## 6. 建议 commit message

```text
chore: add v2e DID revision planning assets
```


---

## 7. 2026-04-20 人工确认后的新增交付

### 7.1 派生模板

- `appendix_A0_city_year_treatment_registry_template.csv/.xlsx`
- `appendix_A1_province_year_treat_share_audit_template.csv/.xlsx`
- `appendix_A2_treatment_threshold_audit_template.csv/.xlsx`
- `appendix_A3_independent_mechanism_variable_template.csv/.xlsx`
- `appendix_A4_text_validity_audit_template.csv/.xlsx`
- `appendix_A0_A4_templates_codebook.md`
- `appendix_A2_treat_share_aggregation_audit_note.md`

说明：模板为空表头，不包含伪造城市名单或阈值。默认审计权重为等权城市计数 `aggregation_weight=1`。

### 7.2 DID 文献元数据

- `v2e_DID_14_literature_metadata.csv`
- `v2e_DID_14_literature_metadata.json`
- `v2e_DID_14_literature_metadata_report.md`

说明：已解析 14 个 PDF，但正式参考文献条目仍需人工/数据库核验。

### 7.3 rerun 与结果快照

- `rerun_logs/rerun_status_summary.md`
- `rerun_logs/rerun_status_summary_utf8.csv/.json`
- `rerun_logs/*.utf8.log`
- `v2e_rerun_result_snapshot.csv`
- `v2e_rerun_result_snapshot.md`

实际运行：baseline audit、trend-adjusted DID、leave-one-province-out、wild cluster bootstrap、robustness defense summary 均退出码 0。log-ratio 未发现可直接运行脚本，未产生新结果。

### 7.4 修改过的共享脚本

- `PPP_empirical_reinforcement_bundle_20260416_unified_v3/bundle_common.py`

修改目的：修复 rerun 路径解析中 `.docx` 多重匹配问题，明确锚定 20260418 对象保留投稿版。该修改不改变模型公式、变量定义或原始数据。

### 7.5 高风险文件仍未修改

- 未覆盖 `v2d_DID_冲刺修订报告_可下载版.docx`。
- 未覆盖任何主文稿 `.docx`。
- 未修改 `数据总表（一切数据基础）.xlsx`。
- 未修改 `ppp论文数据/PPP_v3结果层状态表_20260413_1345.xlsx`。
- 未修改 `ppp论文数据/PPP_变量与模型最终采用口径表_20260413_1345.xlsx`。
- 未修改 `.env`、密钥、生产配置。


---

## 8. Git diff 审查提示

本轮未 commit、未 push。当前工作区除 v2e 文本资产外，还包含 full rerun 产生或更新的派生资产：

- 更新的补强包结果工作簿：`unified_baseline_reference.xlsx`、`trend_adjusted_did_results.xlsx`、`leave_one_province_out_results.xlsx`、`leave_one_province_out_stability_summary.xlsx`、`wild_cluster_bootstrap_summary.xlsx`、`robustness_defense_summary.xlsx`。
- 新生成的 Figure 8A/8B 诊断图和 manuscript 图：PNG/SVG/PDF 各格式。
- `bundle_common.py` 的最小路径锚定修复。

这些二进制 `.xlsx` / 图形文件无法进行行级 diff；已在 `v2e_rerun_result_snapshot.csv/.md` 中提供可审查数值快照。若下一步需要干净提交，建议先人工确认是否把这些二进制 rerun 输出一并纳入 commit。

---

## 9. 新增派生审计数据交付（2026-04-20 19:26）

根据人工确认，本轮已将“可用的省年审计数据”和“伪 city-slot registry”放入 v2e 执行包目录：

- `v2e_province_year_treat_share_audit_from_v2d.csv`
- `v2e_province_year_treat_share_audit_from_v2d.xlsx`
- `v2e_implied_city_slot_registry_from_v2d_treat_share.csv`
- `v2e_implied_city_slot_registry_from_v2d_treat_share.xlsx`
- `v2e_implied_registry_construction_summary.json`
- `v2e_implied_registry_construction_report.md`

交付性质：这些是从 v2d 省年重构表反推的派生审计数据，适合用于聚合链条审计、rerun 前接口测试和附录透明化说明；它们不是原始城市名单，也不是处理阈值底表。当前权重按等权 city-slot 设置，因为仓库内没有可核实的城市权重底表，且现有 treat_share 与城市计数份额相匹配。

未做事项：未覆盖 v2d 原始资产，未改原始数据总表，未改任何原始 `.docx`/`.xlsx` 主文件，未把派生数据写成正式结论。



---

## Working proxy analysis update（2026-04-20 20:02:42）

- 已按人工确认使用 implied city-slot registry 与 province-year audit 生成 working proxy data outputs。
- 详见 `v2e_working_proxy_analysis_report.md` 与 `v2e_working_proxy_analysis_summary.json`。
- 机制变量与文本效度不由 registry/threshold 自动生成；已生成可得性矩阵并保留不能估计项。
