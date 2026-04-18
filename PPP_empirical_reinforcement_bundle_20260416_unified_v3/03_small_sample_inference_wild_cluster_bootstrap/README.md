# Wild cluster bootstrap / small-sample inference module

## Purpose

This module provides a conservative appendix-level inference check for the baseline DID results.

## Input

Expected local input inside this module:

- `inputs/wild_cluster_bootstrap_input_summary.xlsx`

For compatibility, if only the old file name `inputs/baseline_did_bootstrap_or_permutation_pvalues.xlsx` exists, the script copies it to the canonical input name before processing.

## Run

```bash
python PPP_empirical_reinforcement_bundle_20260416_unified_v3/03_small_sample_inference_wild_cluster_bootstrap/scripts/summarize_small_sample_inference.py
```

## Outputs

- `tables/wild_cluster_bootstrap_summary.xlsx`
- `text/small_sample_inference_body_insert.md`
- `notes/small_sample_inference_notes.md`

## Manuscript rule

This layer is not a replacement main model and should not sit on the same level as Figure 8A / Figure 8B.
