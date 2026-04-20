# v2e 派生模板说明：Treatment Registry / 聚合审计 / 机制与文本效度

> 状态：模板已生成；未填入真实城市名单、阈值底表或回归结果。未重跑，不得当作结果。

## 1. 已生成模板

- `appendix_A0_city_year_treatment_registry_template.csv/.xlsx`
- `appendix_A1_province_year_treat_share_audit_template.csv/.xlsx`
- `appendix_A2_treatment_threshold_audit_template.csv/.xlsx`
- `appendix_A3_independent_mechanism_variable_template.csv/.xlsx`
- `appendix_A4_text_validity_audit_template.csv/.xlsx`

## 2. A0：city-year treatment registry

字段：`province`, `city`, `city_id`, `year`, `first_treat_year`, `treated`, `treatment_source`, `source_note`, `aggregation_weight`。

当前人工确认显示：没有原始城市名单，也没有处理阈值底表。因此本轮只生成空模板，不伪造城市名单。若后续无法取得城市权重口径，默认可采用等权城市计数，即 `aggregation_weight = 1`。这一设置只能作为可复核默认假设，不能写成既有事实。

## 3. A1：province-year treat_share 聚合审计

字段包括：处理城市数、可纳入城市总数、权重和、重算 treat_share、当前 treat_share、差异、聚合规则、阈值规则与审计标记。

建议的默认公式：

`treated_city_count = sum(treated)`

`eligible_city_count = count(city_id)`

`weight_sum = sum(aggregation_weight)`

`如果无权重：treat_share_recomputed = treated_city_count / eligible_city_count`

`如果有权重：treat_share_recomputed = sum(treated * aggregation_weight) / sum(aggregation_weight)`

## 4. A2：阈值底表审计

因用户确认当前无处理阈值底表，本轮只保留字段设计。后续若确有原始政策名单、项目启动阈值或文本命中阈值，应补充：原始信号变量、阈值规则、阈值数值、处理状态、来源文件与来源工作表。

## 5. A3：独立机制变量模板

候选变量仅作为数据需求设计，不构成已验证机制结果：审批时长、采购到执行间隔、公告披露完整度、项目退库率、在线服务指数、项目执行周期等。

## 6. A4：文本变量效度审计模板

用于人工双标注、Cohen's kappa / Krippendorff's alpha、替代词典稳定性、主题稳定性与外部对照。若无人工标注数据，只能作为审计方案和模板，不能声称 A/B/C/D 文本变量已通过强机制检验。
