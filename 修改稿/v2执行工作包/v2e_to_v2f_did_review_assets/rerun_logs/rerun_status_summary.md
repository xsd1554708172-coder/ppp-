# v2f rerun status summary

| name | returncode | ok | log |
|---|---|---|---|
| 01_unified_baseline_reference | 0 | True | 修改稿/v2执行工作包/v2e_to_v2f_did_review_assets/rerun_logs/01_unified_baseline_reference.log |
| 02_trend_adjusted_DID | 0 | True | 修改稿/v2执行工作包/v2e_to_v2f_did_review_assets/rerun_logs/02_trend_adjusted_DID.log |
| 03_leave_one_province_out | 0 | True | 修改稿/v2执行工作包/v2e_to_v2f_did_review_assets/rerun_logs/03_leave_one_province_out.log |
| 04_wild_cluster_bootstrap_summary | 0 | True | 修改稿/v2执行工作包/v2e_to_v2f_did_review_assets/rerun_logs/04_wild_cluster_bootstrap_summary.log |
| 05_robustness_defense_summary | 0 | True | 修改稿/v2执行工作包/v2e_to_v2f_did_review_assets/rerun_logs/05_robustness_defense_summary.log |

## 主快照

| outcome | official_coef | official_p_value | fresh_baseline_coef | fresh_baseline_se | fresh_baseline_p_value | fresh_baseline_nobs | trend_adjusted_coef | trend_adjusted_p_value | placebo_2015_coef | placebo_2015_p_value | role |
|---|---|---|---|---|---|---|---|---|---|---|---|
| exec_share | 0.3556 | 0.0003845 | 0.3600 | 0.1008 | 0.0012 | 262 | 0.2263 | 0.2044 | 0.1724 | 0.3558 | official_anchor_plus_fresh_audit |
| proc_share | -0.4023 | 7.9e-05 | -0.4065 | 0.1023 | 0.00041 | 262 | -0.3521 | 0.0577 | -0.1620 | 0.3970 | official_anchor_plus_fresh_audit |
| ppp_quality_zindex | 0.5253 | 0.2126 | 0.5226 | 0.4515 | 0.2562 | 262 | -0.1699 | 0.6810 | 0.2629 | 0.2171 | official_anchor_plus_fresh_audit |
| log_ratio_exec_proc |  |  | 3.2103 | 1.4609 | 0.0358 | 262 |  |  |  |  | log_ratio_diagnostic_c=0.0033557047 |

## randomization

| outcome | actual_fresh_baseline_coef | n_permutations_successful | two_sided_empirical_p | role |
|---|---|---|---|---|
| exec_share | 0.3600 | 199 | 0.3350 | randomization_diagnostic_not_main |
| proc_share | -0.4065 | 199 | 0.2700 | randomization_diagnostic_not_main |
| ppp_quality_zindex | 0.5226 | 199 | 0.4250 | randomization_diagnostic_not_main |

## fractional response

| outcome | specification | coef | p_value | nobs | status | role |
|---|---|---|---|---|---|---|
| exec_share | fractional_logit_binomial_fe | 3.3665 | 0.0811 | 262 | completed_exploratory | bounded_share_diagnostic_not_main |
| proc_share | fractional_logit_binomial_fe | -5.4059 | 0.0117 | 262 | completed_exploratory | bounded_share_diagnostic_not_main |
