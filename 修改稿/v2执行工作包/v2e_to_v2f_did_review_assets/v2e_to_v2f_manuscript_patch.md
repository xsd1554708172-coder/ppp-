# v2e -> v2f manuscript patch

## 摘要/识别策略替换原则
将“证明”“治理质量整体跃升”“平行趋势已获充分支持”等强表述，替换为“连续处理强度下的平均条件关联”“防御性稳健性支持”“边界性结果”“政策文本证据线索”。

## 第4章识别策略替换段
> 鉴于处理变量是省年层面的连续暴露强度，本文不将估计量解释为标准二元处理 ATT，而将其界定为连续处理强度下的平均条件关联证据。省份固定效应吸收时间不变地区差异，年份固定效应吸收共同冲击；趋势调整、留一省、wild cluster bootstrap、log-ratio、placebo/randomization 和 fractional response 均作为防御性稳健性或边界诊断，不替代主识别。

## 第5章事件研究替换段
> 事件研究图用于呈现处理强度变化前后的动态路径和识别边界。本文不据此宣称平行趋势已经成立；若政策前动态项存在波动，解释为需要谨慎处理的诊断信号。

## 快照
| outcome | official_coef | official_p_value | fresh_baseline_coef | fresh_baseline_se | fresh_baseline_p_value | fresh_baseline_nobs | trend_adjusted_coef | trend_adjusted_p_value | placebo_2015_coef | placebo_2015_p_value | role |
|---|---|---|---|---|---|---|---|---|---|---|---|
| exec_share | 0.3556 | 0.0003845 | 0.3600 | 0.1008 | 0.0012 | 262 | 0.2263 | 0.2044 | 0.1724 | 0.3558 | official_anchor_plus_fresh_audit |
| proc_share | -0.4023 | 7.9e-05 | -0.4065 | 0.1023 | 0.00041 | 262 | -0.3521 | 0.0577 | -0.1620 | 0.3970 | official_anchor_plus_fresh_audit |
| ppp_quality_zindex | 0.5253 | 0.2126 | 0.5226 | 0.4515 | 0.2562 | 262 | -0.1699 | 0.6810 | 0.2629 | 0.2171 | official_anchor_plus_fresh_audit |
| log_ratio_exec_proc |  |  | 3.2103 | 1.4609 | 0.0358 | 262 |  |  |  |  | log_ratio_diagnostic_c=0.0033557047 |
