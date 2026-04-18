# Trend-Adjusted DID Module

This module is a defensive robustness layer. The canonical main identification remains `treat_share` DID/TWFE.

## Inputs
- Unified baseline reference: `00_unified_baseline_reference/unified_baseline_reference.xlsx`
- Formal V3 panel: `ppp论文数据/01_第3到第8部分_最终修正版/第5部分_核心实证识别/（5.1）识别框架、并表与模型设定/PPP_3.6_model_ready_panel_v3_统一口径_方案2_实际执行版_20260413_1048.csv`
- Baseline anchor table: `ppp论文数据/01_第3到第8部分_最终修正版/第5部分_核心实证识别/（5.3）基准多期DID_TWFE正式回归/PPP_第5部分_5.3正式回归结果长表_V3_重估版_20260413_1048.csv`

## Model
`y ~ treat_share + dfi + digital_econ + ln_rd_expenditure + ln_tech_contract_value + ln_patent_grants + C(province) + C(year) + C(province):year_idx`

## Outputs
- `tables/trend_adjusted_did_results.xlsx`
- `figures/Figure_5_baseline_vs_trend_adjusted_forest.png`
- `text/trend_adjusted_did_body_insert.md`
- `notes/trend_adjusted_did_notes.md`
- `scripts/README.md`

## Canonical reading
- `exec_share`: direction stays positive, significance weakens under province trends.
- `proc_share`: remains negative and statistically meaningful under the current trend-adjusted specification.
- `ppp_quality_zindex`: stays weaker and cannot be promoted to the main conclusion.
