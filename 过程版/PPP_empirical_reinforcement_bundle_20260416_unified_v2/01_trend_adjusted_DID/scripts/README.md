# Trend-adjusted DID module

Run from the workspace root:

```bash
python PPP_empirical_reinforcement_bundle_20260416_unified_v2/01_trend_adjusted_DID/scripts/run_trend_adjusted_did.py
```

This module reruns the official baseline DID sample and adds province-specific linear trends:

```text
outcome ~ treat_share + controls + C(province) + C(year) + C(province):year_idx
```

Outputs:
- `tables/trend_adjusted_did_results.xlsx`
- `figures/Figure_8A_baseline_vs_trend_adjusted_forest.png`
- `text/trend_adjusted_did_body_insert.md`
- `notes/trend_adjusted_did_notes.md`
