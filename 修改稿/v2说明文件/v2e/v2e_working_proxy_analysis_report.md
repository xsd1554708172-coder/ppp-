# v2e working proxy analysis report

> 生成时间：2026-04-20 20:02:01
> 本文件落实人工确认：在真实 city-year treatment registry 与处理阈值底表缺失的情况下，v2e 将采用 implied city-slot registry 与 province-year audit 作为**工作分析输入**。这不是把它们改写为真实原始数据，而是在所有输出中显式标注其 proxy/implied 身份。

## 1. 已采用的工作输入

- Working registry：`C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\修改稿\v2修改建议\v2e修改建议\v2e_implied_city_slot_registry_from_v2d_treat_share.csv`
- Working threshold/audit proxy：`C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\修改稿\v2修改建议\v2e修改建议\v2e_province_year_treat_share_audit_from_v2d.csv`

## 2. 新增输出

- Working threshold proxy：`v2e_working_threshold_proxy_from_province_year_audit.csv` / `v2e_working_threshold_proxy_from_province_year_audit.xlsx`
- Registry year summary：`v2e_working_registry_analysis_by_year.csv` / `v2e_working_registry_analysis_by_year.xlsx`
- Registry province summary：`v2e_working_registry_analysis_by_province.csv` / `v2e_working_registry_analysis_by_province.xlsx`
- Independent mechanism availability matrix：`v2e_independent_mechanism_variable_availability_matrix.csv` / `v2e_independent_mechanism_variable_availability_matrix.xlsx`
- Text validity data availability matrix：`v2e_text_validity_data_availability_matrix.csv` / `v2e_text_validity_data_availability_matrix.xlsx`
- Summary JSON：`v2e_working_proxy_analysis_summary.json`
- Project disclosure completeness proxy：`v2e_project_disclosure_completeness_proxy_by_province_year.csv` / `v2e_project_disclosure_completeness_proxy_by_province_year.xlsx`

## 3. 核心数量核查

- Province-year audit rows：266
- Implied city-slot rows：2870
- Working threshold proxy rows：266
- Use-for-analysis rows：258
- Missing-city-n rows：8
- Year summary rows：9
- Province summary rows：32

## 4. 对用户 1/2/3 的落实

1. 真实城市名单缺失时，`v2e_implied_city_slot_registry_from_v2d_treat_share.*` 被采用为 v2e working registry，用于聚合链条审计和后续可执行数据分析。
2. 处理阈值底表缺失时，`v2e_province_year_treat_share_audit_from_v2d.*` 被采用为 working threshold/audit proxy；它提供的是省年可审计的 eligible count、integer coverage count 与 share，而不是原始政策阈值。
3. implied registry 不再只停留在空模板/占位层，而是作为本轮 working analysis input；但所有表和正文必须保留 implied/proxy 标识，不能写成真实城市名单。

## 5. 对独立机制变量的判断

独立机制变量通常**不依赖** city-year registry 或处理阈值底表，而依赖独立的项目过程、审批、公告、在线服务或里程碑数据。因此，不能仅凭 implied registry/audit 生成审批时长、采购到执行间隔、项目退库率、在线服务指数或项目执行周期。

本轮能做的最接近可行项是：若项目级底表包含 `项目概况`、`合作范围`、`批复意见` 等字段，则生成“公告/披露完整度 proxy”。该 proxy 已生成与否见 summary JSON；它只能作为候选机制变量的数据准备，不构成正式机制估计。

## 6. 对文本效度审计的判断

文本效度审计也**不依赖** city-year registry 或处理阈值底表。人工双标注、Cohen's kappa / Krippendorff's alpha 需要同一文档的两名或多名人工编码者标签。当前发现的是试编码矩阵、词典、W2V 扩词和 BERTopic 输出，尚未发现可直接计算 kappa/alpha 的成对人工标注数据。因此本轮只生成 text validity data availability matrix，不伪造一致性系数。

## 7. DID 文献核验处理

按人工确认，若 14 篇 DID 文献逐篇元数据核验对当前正文推进帮助有限，则本轮不把它作为阻塞项；已有文献整合 patch 保留，但不强制继续逐篇解析。

## 8. 写作边界

- 可写：v2e 使用 implied registry 与 province-year audit 形成可执行、可审计的处理链条工作输入。
- 不可写：已经恢复真实城市名单、已经找到原始阈值底表、已经完成城市层面因果识别。
- 主识别仍然只能是 `treat_share` 多期 DID/TWFE。
