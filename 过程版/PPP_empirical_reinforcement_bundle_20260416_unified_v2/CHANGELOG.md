# CHANGELOG

## 2026-04-17 unified v2

- Added `00_unified_baseline_reference` to lock one canonical baseline DID reference against the formal 5.3 long table.
- Rebuilt `01_trend_adjusted_DID` as a fully reproducible module tied to the same formal sample and control set as table 4.
- Rebuilt `02_leave_one_province_out_jackknife` as a fully reproducible module with cleaned outputs and defensively worded notes.
- Downgraded `03_small_sample_inference_wild_cluster_bootstrap` to an appendix-level support layer with cleaned wording.
- Added `04_manuscript_integration` outputs for section 5.6 replacement text, abstract/conclusion additions, and table/figure note updates.
- Kept the main paper constraint unchanged: `treat_share` DID / TWFE remains the only main identification strategy.
