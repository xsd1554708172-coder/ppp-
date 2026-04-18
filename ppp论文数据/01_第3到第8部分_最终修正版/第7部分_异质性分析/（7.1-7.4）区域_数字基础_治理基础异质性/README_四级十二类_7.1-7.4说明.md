# 第7部分 7.1–7.4 异质性分析（V2 四级十二类）

- 面板文件：`PPP_3.6_model_ready_panel_v2_四级十二类_实际执行版.csv`
- 识别方式：省-年 TWFE
- 固定效应：province FE + year FE
- 聚类：province
- 控制变量：dfi, digital_econ, base_station_density, software_gdp_share, it_service_gdp_share, ln_rd_expenditure, ln_tech_contract_value, ln_patent_grants
- 样本量：262

## 本批分组
- 区域：东部 / 中部 / 西部
- 数字经济高低：按省级样本期平均 `digital_econ` 中位数划分
- 数字金融高低：按省级样本期平均 `dfi` 中位数划分
- 治理基础高低：按 2014–2015 年 `ppp_quality_zindex` 省级均值中位数划分

## 当前结果概览
- `exec_share`：交互项整体不强，数字金融高低交互项边际显著（p≈0.058），其余差异不稳。
- `proc_share`：交互项整体不强，未观察到稳定显著的条件差异主导。
- `ppp_quality_zindex`：数字金融高低交互项显著（p<0.001），数字经济高低交互项边际显著（p≈0.076），其余差异不稳。

## 写作建议
- 正文优先强调：主效应并未明显集中于单一区域或单一基础条件，异质性更像“条件差异线索”而非“主导来源”。
- 区域分组的组内样本量较小、固定效应较多，分组系数波动偏大；正文更适合把区域结果降调处理。
- 若需保守写法，可表述为：改革效应具有一定普遍性，在数字金融/数字经济基础较高地区，对质量型结果的表现相对更敏感，但证据不宜过度放大。
