# Trend-adjusted DID module

## Purpose

This module rebuilds the main defensive robustness layer used in manuscript section 5.6.1.

## Specification

- Same formal sample as Table 4: `baseline_sample_5_3 == 1`
- Same treatment: `treat_share`
- Same controls as the official baseline DID
- Same province/year fixed effects
- Additional defense term: province-specific linear time trends

## Inputs

This bundle is not self-extracting. Before running, the following formal files must already exist somewhere under the workspace root:

- `PPP_3.6_model_ready_panel_v3_统一口径_方案2_实际执行版_20260413_1048.csv`
- `PPP_第5部分_5.3正式回归结果长表_V3_重估版_20260413_1048.csv`
- `00_unified_baseline_reference/tables/unified_baseline_reference.xlsx`

If the workspace still only contains compressed archives, extract them first. The script will fail loudly if the required files are missing.

## Run

```bash
python PPP_empirical_reinforcement_bundle_20260416_unified_v3/01_trend_adjusted_DID/scripts/run_trend_adjusted_did.py
```

## Outputs

- `tables/trend_adjusted_did_results.xlsx`
- `text/trend_adjusted_did_body_insert.md`
- `notes/trend_adjusted_did_notes.md`

The final clean figure assets used for manuscript integration are exported by:

```bash
python PPP_empirical_reinforcement_bundle_20260416_unified_v3/04_manuscript_integration/scripts/export_final_figures_20260417_1537.py
```

That script writes:

- `figures/Figure_8A_trend_adjusted_did_20260417_1537.(png|svg)` for the paper-facing version
- `figures/Figure_8A_trend_adjusted_did_diagnostic_20260417_1537.(png|svg)` for the engineering diagnostic version
