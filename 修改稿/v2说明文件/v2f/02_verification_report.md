# v2f Verification Report

## 输入抽取
```json
{
  "did_method_review": {
    "exists": true,
    "paragraphs": 111,
    "tables": 15,
    "characters": 12161
  },
  "v2e_review": {
    "exists": true,
    "paragraphs": 56,
    "tables": 4,
    "characters": 12082
  }
}
```

## rerun 命令
| name | returncode | ok | log |
|---|---|---|---|
| 01_unified_baseline_reference | 0 | True | 修改稿/v2执行工作包/v2e_to_v2f_did_review_assets/rerun_logs/01_unified_baseline_reference.log |
| 02_trend_adjusted_DID | 0 | True | 修改稿/v2执行工作包/v2e_to_v2f_did_review_assets/rerun_logs/02_trend_adjusted_DID.log |
| 03_leave_one_province_out | 0 | True | 修改稿/v2执行工作包/v2e_to_v2f_did_review_assets/rerun_logs/03_leave_one_province_out.log |
| 04_wild_cluster_bootstrap_summary | 0 | True | 修改稿/v2执行工作包/v2e_to_v2f_did_review_assets/rerun_logs/04_wild_cluster_bootstrap_summary.log |
| 05_robustness_defense_summary | 0 | True | 修改稿/v2执行工作包/v2e_to_v2f_did_review_assets/rerun_logs/05_robustness_defense_summary.log |


## fresh diagnostics
- 快照：`修改稿/v2执行工作包/v2e_to_v2f_did_review_assets/result_snapshots/v2f_empirical_diagnostics_snapshot.xlsx`
- log-ratio continuity correction：`0.00335570469798655`
- baseline nobs：`262`

| outcome | official_coef | official_p_value | fresh_baseline_coef | fresh_baseline_se | fresh_baseline_p_value | fresh_baseline_nobs | trend_adjusted_coef | trend_adjusted_p_value | placebo_2015_coef | placebo_2015_p_value | role |
|---|---|---|---|---|---|---|---|---|---|---|---|
| exec_share | 0.3556 | 0.0003845 | 0.3600 | 0.1008 | 0.0012 | 262 | 0.2263 | 0.2044 | 0.1724 | 0.3558 | official_anchor_plus_fresh_audit |
| proc_share | -0.4023 | 7.9e-05 | -0.4065 | 0.1023 | 0.00041 | 262 | -0.3521 | 0.0577 | -0.1620 | 0.3970 | official_anchor_plus_fresh_audit |
| ppp_quality_zindex | 0.5253 | 0.2126 | 0.5226 | 0.4515 | 0.2562 | 262 | -0.1699 | 0.6810 | 0.2629 | 0.2171 | official_anchor_plus_fresh_audit |
| log_ratio_exec_proc |  |  | 3.2103 | 1.4609 | 0.0358 | 262 |  |  |  |  | log_ratio_diagnostic_c=0.0033557047 |


## 红线核验
- 主识别仍为 `treat_share` 多期 DID/TWFE。
- trend-adjusted DID、leave-one-province-out、wild bootstrap、log-ratio、placebo/randomization、fractional response 均只作防御性稳健性或边界诊断。
- 未把 event study 写成证明动态可比性已获充分支持。
- 未把 `ppp_quality_zindex` 写成治理质量全面提升。
- 未把 A/B/C/D 写成独立机制识别。
- 未修改 v1、原始数据总表或正式 source-of-truth xlsx。

## Word 公式规则
v2f Word 从 v2e 对象保留公式版复制并插入无公式说明段；保留 Office Math 对象，未向 Word 新增纯文本公式。
