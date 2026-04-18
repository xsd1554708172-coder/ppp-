# 第7部分 7.5 PPP 风险暴露异质性（V2 四级十二类）

- 面板文件：`PPP_3.6_model_ready_panel_v2_四级十二类_实际执行版.csv`
- 识别方式：省-年 TWFE
- 固定效应：province FE + year FE
- 聚类：province
- 控制变量：dfi, digital_econ, base_station_density, software_gdp_share, it_service_gdp_share, ln_rd_expenditure, ln_tech_contract_value, ln_patent_grants
- 样本量：262

## 风险暴露代理口径
- 使用**处理前（2014–2015）省级 `ppp_norm_risk_index` 均值**作为 PPP 风险暴露代理。
- 按中位数 **0.043426** 划分高/低风险暴露组。
- 这样做是为了避免把改革后的文本变化直接用于异质性分组。

## 本批核心发现
- `exec_share`：交互项不显著（p=0.3676）；低风险暴露组主效应显著为正，高风险暴露组不显著。
- `proc_share`：交互项不显著（p=0.3369）；低风险暴露组主效应显著为负，高风险暴露组不显著。
- `ppp_quality_zindex`：交互项不显著（p=0.9160）；未观察到稳定的风险暴露异质性。

## 结论写法建议
- 更适合写为：**风险暴露异质性证据有限，主效应具有一定普遍性；已观测到的组间差异更多表现为低风险暴露组系数更稳定。**
- 不宜写成：高风险暴露组显著放大或主导了改革效应。
