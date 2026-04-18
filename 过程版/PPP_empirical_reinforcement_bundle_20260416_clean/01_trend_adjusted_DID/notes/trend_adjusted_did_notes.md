# Trend-Adjusted DID Notes

## Purpose
This module does not replace the canonical `treat_share` DID/TWFE design. It adds province-specific linear trends as a defensive robustness layer.

## Data and sample
- Unified baseline reference: `00_unified_baseline_reference/unified_baseline_reference.xlsx`
- Formal V3 main panel: `ppp论文数据/01_第3到第8部分_最终修正版/第5部分_核心实证识别/（5.1）识别框架、并表与模型设定/PPP_3.6_model_ready_panel_v3_统一口径_方案2_实际执行版_20260413_1048.csv`
- Estimation sample: `baseline_sample_5_3 == 1`
- Cluster unit: `province`

## Specification
- Baseline RHS is unchanged.
- Added term: province-specific linear trends via `C(province):year_idx`.
- Controls: `dfi`, `digital_econ`, `ln_rd_expenditure`, `ln_tech_contract_value`, `ln_patent_grants`

## Reference result summary
- `exec_share`: 0.226286, p=0.194479
- `proc_share`: -0.352107, p=0.048464
- `ppp_quality_zindex`: -0.169935, p=0.677999
