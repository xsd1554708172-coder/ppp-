from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
import sys

sys.path.insert(0, str(ROOT))

from bundle_common import (  # noqa: E402
    AUDIT_BASELINE_SHEET,
    CANONICAL_BASELINE_SHEET,
    SPEC_ANCHOR_SHEET,
    TREATMENT,
    build_audit_rerun_reference,
    build_manuscript_baseline_reference,
    build_spec_anchor,
    clean_baseline_sample,
    load_main_panel,
    read_official_baseline_rows,
    resolve_paths,
    rerun_baseline_reference,
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

    official = read_official_baseline_rows(paths.baseline_long_table)
    rerun = rerun_baseline_reference(base_df)
    manuscript_baseline = build_manuscript_baseline_reference(official)
    audit_rerun = build_audit_rerun_reference(official, rerun)
    spec_anchor = build_spec_anchor(base_df)

    output = table_dir / "unified_baseline_reference.xlsx"
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        manuscript_baseline.to_excel(writer, index=False, sheet_name=CANONICAL_BASELINE_SHEET)
        audit_rerun.to_excel(writer, index=False, sheet_name=AUDIT_BASELINE_SHEET)
        spec_anchor.to_excel(writer, index=False, sheet_name=SPEC_ANCHOR_SHEET)

    readme = f"""# Unified baseline DID reference

This folder defines the one canonical baseline reference used across the paper.

## Canonical specification

- Main identification remains: `{TREATMENT}` multi-period DID / TWFE
- Manuscript-facing baseline: official section 5.3 long-table anchor
- Fresh rerun: audit only, not a manuscript replacement
- Sample: `baseline_sample_5_3 == 1`
- Fixed effects: province FE + year FE
- Cluster: province
- Controls: dfi, digital_econ, ln_rd_expenditure, ln_tech_contract_value, ln_patent_grants

## Output workbook

- `tables/unified_baseline_reference.xlsx`

### Sheet roles

- `{CANONICAL_BASELINE_SHEET}`: official 5.3 anchor only, no rerun values
- `{AUDIT_BASELINE_SHEET}`: fresh rerun values and diffs for internal comparison only
- `{SPEC_ANCHOR_SHEET}`: compact canonical specification summary

## Input sources

- Main panel: `{paths.panel_csv.name}`
- Official baseline long table: `{paths.baseline_long_table.name}`
- Current manuscript anchor: `{paths.current_docx.name}`

## Manuscript-facing rule

The manuscript-facing baseline is the official 5.3 long-table anchor. The fresh rerun exists only to confirm whether the active panel and the archived baseline remain numerically aligned; if they differ, downstream text should still quote the official anchor and treat the rerun as engineering audit evidence only.
"""
    (note_dir / "baseline_spec_readme.md").write_text(readme, encoding="utf-8")


if __name__ == "__main__":
    main()
