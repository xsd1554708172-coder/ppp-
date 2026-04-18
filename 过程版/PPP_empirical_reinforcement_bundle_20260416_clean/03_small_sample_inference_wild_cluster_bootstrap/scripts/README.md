# Wild cluster bootstrap / small-sample inference module

This folder contains the conservative inference check for the baseline DID specification.

## Run

From the workspace root:

```bash
python PPP_empirical_reinforcement_bundle_20260416_clean/03_small_sample_inference_wild_cluster_bootstrap/scripts/run_small_sample_inference.py
```

## What it does

- Finds the V3 main panel CSV under the workspace data tree.
- Keeps `baseline_sample_5_3 == 1`.
- Re-estimates the baseline DID with province and year fixed effects.
- Applies a null-imposed province-level wild cluster bootstrap.

## Output files

- `../tables/baseline_did_bootstrap_or_permutation_pvalues.xlsx`
- `../figures/Figure_5_wild_cluster_bootstrap_distribution.png`
- `../notes/small_sample_inference_notes.md`
- `../text/bootstrap_body_insert.md`

## Interpretation

Use this module as a small-sample inference check only. It should be written as supportive but conservative evidence, not as a replacement main model or as a claim that every coefficient stays highly significant under the strictest inference rule.
