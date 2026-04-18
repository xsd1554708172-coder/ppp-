# Leave-one-province-out / jackknife module

Run from the workspace root:

```bash
python PPP_empirical_reinforcement_bundle_20260416_unified_v2/02_leave_one_province_out_jackknife/scripts/run_leave_one_province_out.py
```

This module keeps the official baseline DID specification fixed and repeatedly removes one province at a time.

Outputs:
- `tables/leave_one_province_out_results.xlsx`
- `tables/leave_one_province_out_stability_summary.xlsx`
- `figures/Figure_8B_leave_one_province_out_stability.png`
- `text/leave_one_province_out_body_insert.md`
- `notes/leave_one_province_out_notes.md`
