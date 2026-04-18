# Leave-one-province-out / jackknife module

## Purpose

This module answers a narrow robustness question: whether the core structural results are entirely driven by any single province.

## Inputs

The following files must already exist somewhere under the workspace root:

- `PPP_3.6_model_ready_panel_v3_统一口径_方案2_实际执行版_20260413_1048.csv`
- `00_unified_baseline_reference/tables/unified_baseline_reference.xlsx`

If the workspace still only contains compressed archives, extract them first. The script will fail loudly if the required files are missing.

## Run

```bash
python PPP_empirical_reinforcement_bundle_20260416_unified_v3/02_leave_one_province_out_jackknife/scripts/run_leave_one_province_out.py
```

## Outputs

- `tables/leave_one_province_out_results.xlsx`
- `tables/leave_one_province_out_stability_summary.xlsx`
- `text/leave_one_province_out_body_insert.md`
- `notes/leave_one_province_out_notes.md`

The final clean figure assets used for manuscript integration are exported by:

```bash
python PPP_empirical_reinforcement_bundle_20260416_unified_v3/04_manuscript_integration/scripts/export_final_figures_20260417_1537.py
```

That script writes:

- `figures/Figure_8B_jackknife_stability_20260417_1537.(png|svg)` for the paper-facing version
- `figures/Figure_8B_jackknife_stability_diagnostic_20260417_1537.(png|svg)` for the engineering diagnostic version

## Reading boundary

This is an auxiliary diagnostic layer. It supports sign stability and sample-sensitivity discussion; it does not replace the baseline DID.
