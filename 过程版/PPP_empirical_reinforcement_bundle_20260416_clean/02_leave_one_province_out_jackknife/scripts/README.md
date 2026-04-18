# Leave-one-province-out module

This folder contains the runnable jackknife diagnostic for the baseline DID specification.

## Run

From the workspace root:

```bash
python PPP_empirical_reinforcement_bundle_20260416_clean/02_leave_one_province_out_jackknife/scripts/run_leave_one_province_out.py
```

## What it does

- Finds the V3 main panel CSV under the workspace data tree.
- Keeps `baseline_sample_5_3 == 1`.
- Re-estimates the baseline DID with province and year fixed effects after deleting one province at a time.
- Writes a per-province deletion summary, a stability summary, a figure, a note, and a manuscript replacement text.

## Output files

- `../tables/baseline_did_leave_one_province_out_per_province_deletion_summary.csv`
- `../tables/baseline_did_leave_one_province_out_results.xlsx`
- `../tables/baseline_did_leave_one_province_out_stability_summary.xlsx`
- `../figures/Figure_5_leave_one_province_out_stability.png`
- `../notes/leave_one_province_out_notes.md`
- `../text/leave_one_province_out_body_insert.md`

## Interpretation

Use this module as a robustness check only. It should be written as evidence that the baseline DID is not driven by a single province, not as a replacement main model.
