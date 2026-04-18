# 第6部分 6.1–6.4 机制检验（V2 四级十二类）

- 面板文件：`PPP_3.6_model_ready_panel_v2_四级十二类_实际执行版.csv`
- 识别方式：省-年 TWFE
- 固定效应：province FE + year FE
- 聚类：province
- 控制变量：dfi, digital_econ, base_station_density, software_gdp_share, it_service_gdp_share, ln_rd_expenditure, ln_tech_contract_value, ln_patent_grants
- 一阶段 did 变量：did_intensity, did_any, treat_share
- 主结果方程 did 变量：treat_share, did_any
- 结果变量：ppp_quality_zindex, exec_share, proc_share
- 机制变量：A_idx, B_idx, C_idx, D_idx, ppp_governance_capacity_index, ppp_norm_risk_index
- 样本量：262

## 本批核心发现
- 一阶段上，`treat_share -> A_idx` 为显著正向（coef=170.2099, p=0.0000）。
- 一阶段上，`treat_share -> B_idx` 为显著负向（coef=-303.6780, p=0.0002）。
- 一阶段上，`treat_share -> C_idx` 为显著负向且幅度最大（coef=-526.6563, p=0.0000）。
- 一阶段上，`treat_share -> D_idx` 方向为负，但显著性较弱（coef=-45.2302, p=0.3320）。
- 在将文本机制变量与处理变量同时放入结果方程后，本批主规格下未观察到稳定显著的文本机制变量。
- 因此，本批更适合写成：**改革会改变文本治理结构的一阶段分布，但中介路径目前不宜写成强中介成立**。

## 说明
- 这一版机制检验是新版四级十二类文本变量重建后的第一轮主体机制结果。
- D 类 topic share 仍然偏弱，因此本批主体机制优先使用 `D_idx` 而不是 D 类主题占比。
- 下一步可继续做 6.5 链式机制与 6.6 严格中介分解，但应保持克制，不替代第5部分主识别结论。


## 2026-04-12 v3补充：机制写作边界
- 第6部分应写成“治理结构的文本表达重分布证据”。
- 一阶段显著不等于严格中介已成立。
- 若Bootstrap/Sobel不显著，应作为边界说明而非核心贡献。
