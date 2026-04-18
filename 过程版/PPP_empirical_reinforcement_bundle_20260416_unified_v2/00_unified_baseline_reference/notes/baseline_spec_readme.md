# Unified baseline DID reference

This folder defines the one canonical baseline reference used across all reinforcement modules.

## Canonical specification

- Main identification remains: `treat_share` multi-period DID / TWFE
- Sample: `baseline_sample_5_3 == 1`
- Fixed effects: province FE + year FE
- Cluster: province
- Controls: dfi, digital_econ, ln_rd_expenditure, ln_tech_contract_value, ln_patent_grants

## Purpose

This file is not a new model. It locks the single baseline DID specification that section 5.2 / table 4 already uses, then verifies that every reinforcement module compares back to the same coefficients.

The workbook keeps both:
- the official archived table-4 values (`official_*`), which remain the canonical manuscript reference;
- a fresh rerun on the same formal sample (`coef`, `se`, `p_value`), used only as an engineering cross-check.

If the two differ slightly, manuscript-facing comparison tables and figures should still anchor to the official archived values so that section 5.2, section 5.6, and all reinforcement modules point to the same baseline reference.

## Inputs used

- Main panel: `PPP_3.6_model_ready_panel_v3_统一口径_方案2_实际执行版_20260413_1048.csv`
- Official baseline long table: `PPP_第5部分_5.3正式回归结果长表_V3_重估版_20260413_1048.csv`
- Current manuscript anchor: `PPP论文_完整论文初稿_公共管理风格_修订版_定点替换_20260415.docx`

## Output

- `tables/unified_baseline_reference.xlsx`

Any manuscript-facing comparison should reference the `official_coef`, `official_se`, and `official_p_value` columns from this workbook. The rerun `coef`, `se`, and `p_value` columns are retained only as an engineering cross-check and should not replace the archived baseline used in table 4.
