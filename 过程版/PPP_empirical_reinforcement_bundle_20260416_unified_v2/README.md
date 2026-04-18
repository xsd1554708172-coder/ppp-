# PPP empirical reinforcement bundle (unified v2)

This bundle is the cleaned, manuscript-oriented reinforcement package for section 5.6.

## Design rule

- Main identification remains `treat_share` multi-period DID / TWFE.
- Reinforcement modules are defensive layers only.
- `trend-adjusted DID` is the primary defense layer in the main text.
- `leave-one-province-out` is a sample-driven sensitivity diagnostic.
- `wild bootstrap / small-sample inference` is appendix-level or short-paragraph support.
- `stack DID`, `cohort ATT`, and supplementary dynamic diagnostics remain boundary diagnostics, not replacement models.

## Structure

- `00_unified_baseline_reference/`: single canonical baseline anchor
- `01_trend_adjusted_DID/`: main defensive robustness layer
- `02_leave_one_province_out_jackknife/`: province-driven sensitivity diagnostic
- `03_small_sample_inference_wild_cluster_bootstrap/`: downgraded conservative-inference layer
- `04_manuscript_integration/`: exact replacement text, caption/note updates, and packaging notes

## Run order

From the workspace root:

```bash
python PPP_empirical_reinforcement_bundle_20260416_unified_v2/00_unified_baseline_reference/scripts/build_unified_baseline_reference.py
python PPP_empirical_reinforcement_bundle_20260416_unified_v2/01_trend_adjusted_DID/scripts/run_trend_adjusted_did.py
python PPP_empirical_reinforcement_bundle_20260416_unified_v2/02_leave_one_province_out_jackknife/scripts/run_leave_one_province_out.py
python PPP_empirical_reinforcement_bundle_20260416_unified_v2/03_small_sample_inference_wild_cluster_bootstrap/scripts/summarize_small_sample_inference.py
```

Then use the files under `04_manuscript_integration/` to update the manuscript.
