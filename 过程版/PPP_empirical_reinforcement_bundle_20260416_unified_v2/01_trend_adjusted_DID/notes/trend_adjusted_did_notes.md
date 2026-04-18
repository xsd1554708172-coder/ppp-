# Trend-adjusted DID notes

## Model

- Same sample as table 4: baseline_sample_5_3 == 1
- Same treatment: `treat_share`
- Same controls: dfi, digital_econ, ln_rd_expenditure, ln_tech_contract_value, ln_patent_grants
- Same fixed effects: province FE + year FE
- Additional defense term: province-specific linear trends

## Reading rule

- `proc_share` remains the cleanest defensive result.
- `exec_share` remains directionally aligned but becomes more sensitive once province-specific trends are absorbed.
- `ppp_quality_zindex` remains too unstable for any headline claim.

This module is a defensive robustness layer, not a replacement main model.
