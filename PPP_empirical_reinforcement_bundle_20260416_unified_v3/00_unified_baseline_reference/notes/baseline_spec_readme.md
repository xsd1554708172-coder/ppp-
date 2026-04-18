# Unified baseline DID reference

This folder defines the one canonical baseline reference used across the paper.

## Canonical specification

- Main identification remains: `treat_share` multi-period DID / TWFE
- Manuscript-facing baseline: official section 5.3 long-table anchor
- Fresh rerun: audit only, not a manuscript replacement
- Sample: `baseline_sample_5_3 == 1`
- Fixed effects: province FE + year FE
- Cluster: province
- Controls: dfi, digital_econ, ln_rd_expenditure, ln_tech_contract_value, ln_patent_grants

## Output workbook

- `tables/unified_baseline_reference.xlsx`

### Sheet roles

- `manuscript_baseline`: official 5.3 anchor only, no rerun values
- `audit_rerun`: fresh rerun values and diffs for internal comparison only
- `spec_anchor`: compact canonical specification summary

## Input sources

- Main panel: `PPP_3.6_model_ready_panel_v3_统一口径_方案2_实际执行版_20260413_1048.csv`
- Official baseline long table: `PPP_第5部分_5.3正式回归结果长表_V3_重估版_20260413_1048.csv`
- Current manuscript anchor: `PPP论文_完整论文初稿_公共管理风格_修订版_定点替换_20260415.docx`

## Manuscript-facing rule

The manuscript-facing baseline is the official 5.3 long-table anchor. The fresh rerun exists only to confirm whether the active panel and the archived baseline remain numerically aligned; if they differ, downstream text should still quote the official anchor and treat the rerun as engineering audit evidence only.
