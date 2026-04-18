# PPP empirical reinforcement bundle (unified v3)

This bundle is the manuscript-facing empirical reinforcement package for the PPP paper. It tightens the final defensive robustness layers without changing the paper's main identification strategy.

## Core rule

- The only main identification strategy remains `treat_share` multi-period DID / TWFE.
- All manuscript-facing robustness comparisons must anchor to one baseline only: the official section 5.3 long-table reference stored in `00_unified_baseline_reference/tables/unified_baseline_reference.xlsx`.
- Trend-adjusted DID and leave-one-province-out are defensive robustness layers.
- Wild cluster bootstrap is appendix-level or short boundary support only.
- Stack DID, cohort ATT, and dynamic supplementary identification are boundary diagnostics only and are not elevated in this bundle.

## Bundle structure

- `00_unified_baseline_reference/`
  - one manuscript-facing baseline anchor
  - one internal audit sheet with fresh rerun differences
- `01_trend_adjusted_DID/`
  - trend-adjusted DID rerun
  - engineering figure + manuscript figure
  - body insert + notes
- `02_leave_one_province_out_jackknife/`
  - leave-one-province-out rerun
  - engineering figure + manuscript figure
  - body insert + notes
- `03_small_sample_inference_wild_cluster_bootstrap/`
  - conservative inference summary
  - body insert + notes
- `04_manuscript_integration/`
  - final manuscript patch files
  - table/figure notes
  - robustness summary workbook

## Inputs and preparation

This bundle does **not** auto-extract formal inputs. The scripts assume that the official PPP project files already exist somewhere under the current workspace root.

At minimum, the workspace must contain:

- the official V3 model-ready panel CSV:
  - `PPP_3.6_model_ready_panel_v3_统一口径_方案2_实际执行版_20260413_1048.csv`
- the official section 5.3 long-table CSV:
  - `PPP_第5部分_5.3正式回归结果长表_V3_重估版_20260413_1048.csv`
- the manuscript anchor file:
  - `PPP论文_完整论文初稿_公共管理风格_修订版_定点替换_20260415.docx`
- the canonical small-sample input workbook used by module 03:
  - `PPP_empirical_reinforcement_bundle_20260416_unified_v3/03_small_sample_inference_wild_cluster_bootstrap/inputs/wild_cluster_bootstrap_input_summary.xlsx`

The bundle resolver searches the entire workspace for the first two official files by these exact identifying substrings. The small-sample workbook is expected at the canonical bundle path shown above.

If the workspace only contains compressed archives, extract them first. Scripts will fail loudly when required files are missing or ambiguous.

## Running

From the workspace root:

```bash
python PPP_empirical_reinforcement_bundle_20260416_unified_v3/00_unified_baseline_reference/scripts/build_unified_baseline_reference.py
python PPP_empirical_reinforcement_bundle_20260416_unified_v3/01_trend_adjusted_DID/scripts/run_trend_adjusted_did.py
python PPP_empirical_reinforcement_bundle_20260416_unified_v3/02_leave_one_province_out_jackknife/scripts/run_leave_one_province_out.py
python PPP_empirical_reinforcement_bundle_20260416_unified_v3/03_small_sample_inference_wild_cluster_bootstrap/scripts/summarize_small_sample_inference.py
python PPP_empirical_reinforcement_bundle_20260416_unified_v3/04_manuscript_integration/scripts/build_robustness_defense_summary.py
python PPP_empirical_reinforcement_bundle_20260416_unified_v3/04_manuscript_integration/scripts/export_final_figures_20260417_1537.py
```

## Main manuscript-facing outputs

- `01_trend_adjusted_DID/figures/Figure_8A_trend_adjusted_did_20260417_1537.(png|svg)`
- `02_leave_one_province_out_jackknife/figures/Figure_8B_jackknife_stability_20260417_1537.(png|svg)`
- `04_manuscript_integration/tables/robustness_defense_summary.xlsx`
- `04_manuscript_integration/section_5_6_final.md`
- `04_manuscript_integration/FINAL_MANUSCRIPT_PATCH.md`

## Naming discipline

- manuscript-facing outputs use the official baseline only
- engineering diagnostic outputs are kept separate from manuscript figures
- small-sample files are consistently named `wild_cluster_bootstrap`
