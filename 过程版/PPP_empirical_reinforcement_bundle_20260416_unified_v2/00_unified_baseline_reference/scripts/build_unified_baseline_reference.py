from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
import sys

sys.path.insert(0, str(ROOT))

from bundle_common import (  # noqa: E402
    OUTCOMES,
    TREATMENT,
    clean_baseline_sample,
    load_main_panel,
    read_official_baseline_rows,
    rerun_baseline_reference,
    resolve_paths,
)


def main() -> None:
    paths = resolve_paths(Path(__file__))
    out_dir = Path(__file__).resolve().parents[1]
    table_dir = out_dir / "tables"
    note_dir = out_dir / "notes"
    table_dir.mkdir(parents=True, exist_ok=True)
    note_dir.mkdir(parents=True, exist_ok=True)

    panel = load_main_panel(paths.panel_csv)
    base_df = clean_baseline_sample(panel)

    rerun = rerun_baseline_reference(base_df)
    official = read_official_baseline_rows(paths.baseline_long_table)
    merged = rerun.merge(official, on="outcome", how="left")
    merged["coef_diff_vs_official"] = merged["coef"] - merged["official_coef"]
    merged["se_diff_vs_official"] = merged["se"] - merged["official_se"]
    merged["p_diff_vs_official"] = merged["p_value"] - merged["official_p_value"]
    merged["matches_official_within_tolerance"] = (
        merged[["coef_diff_vs_official", "se_diff_vs_official", "p_diff_vs_official"]]
        .abs()
        .max(axis=1)
        .lt(1e-6)
    )

    output = table_dir / "unified_baseline_reference.xlsx"
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        merged.to_excel(writer, index=False, sheet_name="baseline_reference")
        pd.DataFrame(
            {
                "canonical_main_identification": [f"{TREATMENT} multi-period DID / TWFE"],
                "outcomes": [", ".join(OUTCOMES)],
                "baseline_sample_nobs": [int(base_df.shape[0])],
                "province_count": [int(base_df["province"].nunique())],
                "year_span": [f"{base_df['year'].min()}-{base_df['year'].max()}"],
            }
        ).to_excel(writer, index=False, sheet_name="spec_anchor")

    readme = f"""# Unified baseline DID reference

This folder defines the one canonical baseline reference used across all reinforcement modules.

## Canonical specification

- Main identification remains: `{TREATMENT}` multi-period DID / TWFE
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

- Main panel: `{paths.panel_csv.name}`
- Official baseline long table: `{paths.baseline_long_table.name}`
- Current manuscript anchor: `{paths.current_docx.name}`

## Output

- `tables/unified_baseline_reference.xlsx`

Any manuscript-facing comparison should reference the `official_coef`, `official_se`, and `official_p_value` columns from this workbook. The rerun `coef`, `se`, and `p_value` columns are retained only as an engineering cross-check and should not replace the archived baseline used in table 4.
"""
    (note_dir / "baseline_spec_readme.md").write_text(readme, encoding="utf-8")


if __name__ == "__main__":
    main()
