from __future__ import annotations

from pathlib import Path
import shutil
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from bundle_common import read_manuscript_baseline_reference, resolve_paths  # noqa: E402


CANONICAL_INPUT_NAME = "wild_cluster_bootstrap_input_summary.xlsx"
LEGACY_INPUT_NAME = "baseline_did_bootstrap_or_permutation_pvalues.xlsx"


def prepare_input(input_dir: Path) -> Path:
    canonical = input_dir / CANONICAL_INPUT_NAME
    legacy = input_dir / LEGACY_INPUT_NAME
    if canonical.exists():
        return canonical
    if legacy.exists():
        shutil.copyfile(legacy, canonical)
        return canonical
    raise FileNotFoundError(
        "Wild cluster bootstrap source workbook not found. Expected one of: "
        f"{canonical.name}, {legacy.name}"
    )


def main() -> None:
    paths = resolve_paths(Path(__file__))
    out_root = Path(__file__).resolve().parents[1]
    table_dir = out_root / "tables"
    note_dir = out_root / "notes"
    text_dir = out_root / "text"
    input_dir = out_root / "inputs"
    for p in [table_dir, note_dir, text_dir, input_dir]:
        p.mkdir(parents=True, exist_ok=True)

    src = prepare_input(input_dir)
    raw = pd.read_excel(src, sheet_name="paper_ready_summary")

    keep = [
        "outcome",
        "N",
        "clusters_province",
        "wild_bootstrap_coef",
        "wild_bootstrap_cluster_se",
        "wild_bootstrap_t",
        "wild_bootstrap_p",
        "direction_same_as_baseline",
        "note",
    ]
    missing = [c for c in keep if c not in raw.columns]
    if missing:
        raise KeyError(f"Missing expected columns in bootstrap workbook: {missing}")

    summary = raw[keep].rename(
        columns={
            "wild_bootstrap_coef": "wild_cluster_bootstrap_coef",
            "wild_bootstrap_cluster_se": "wild_cluster_bootstrap_cluster_se",
            "wild_bootstrap_t": "wild_cluster_bootstrap_t",
            "wild_bootstrap_p": "wild_cluster_bootstrap_p_value",
        }
    )

    canonical = read_manuscript_baseline_reference(paths.bundle_root)
    summary = summary.merge(
        canonical[
            ["outcome", "official_coef", "official_se", "official_p_value", "official_nobs"]
        ],
        on="outcome",
        how="left",
    ).rename(
        columns={
            "official_coef": "canonical_baseline_coef",
            "official_se": "canonical_baseline_se",
            "official_p_value": "canonical_baseline_p_value",
            "official_nobs": "canonical_baseline_nobs",
        }
    )

    summary["module_role"] = "appendix_level_support"
    summary["reading_rule"] = [
        "方向保持一致，但在更保守的小样本推断下统计强度更敏感"
        if row["direction_same_as_baseline"]
        else "若方向不再一致，则不应继续作为正文强化证据"
        for _, row in summary.iterrows()
    ]
    summary.to_excel(table_dir / "wild_cluster_bootstrap_summary.xlsx", index=False)

    note = """# Wild cluster bootstrap notes

本层检验的定位是附录级或正文短段级的边界说明，不与趋势调整 DID 或 leave-one-province-out 处于同一层级。

阅读规则：
- 关注核心推进结构结果在更保守推断下是否仍保持方向一致；
- 如果 p 值明显上升，只能写成“统计强度更敏感”，不能反向包装为新的强化证据；
- 质量型结果若继续不稳，只能继续降格处理。

命名口径统一为 `wild cluster bootstrap`。不再混用 `bootstrap_or_permutation` 之类模糊命名。
"""
    (note_dir / "small_sample_inference_notes.md").write_text(note, encoding="utf-8")

    exec_row = summary.loc[summary["outcome"] == "exec_share"].iloc[0]
    proc_row = summary.loc[summary["outcome"] == "proc_share"].iloc[0]
    qual_row = summary.loc[summary["outcome"] == "ppp_quality_zindex"].iloc[0]
    body = f"""# Wild cluster bootstrap 正文短段替换文本

在更保守的小样本推断下，`exec_share` 与 `proc_share` 的方向仍与基准 DID 保持一致，但 wild cluster bootstrap p 值分别为 {exec_row['wild_cluster_bootstrap_p_value']:.3f} 与 {proc_row['wild_cluster_bootstrap_p_value']:.3f}，说明核心推进结构结果在更保守推断下并未反向，但统计强度明显更为敏感。相比之下，`ppp_quality_zindex` 的 wild cluster bootstrap p 值为 {qual_row['wild_cluster_bootstrap_p_value']:.3f}，继续不支持将质量型口径写成稳健主结论。

据此，本层结果更适合作为正文短段或附录级支持，用于补充边界意识，而不应与主识别或主打防守层处于同一层级。
"""
    (text_dir / "small_sample_inference_body_insert.md").write_text(
        body, encoding="utf-8"
    )

    readme = f"""# Wild cluster bootstrap / small-sample inference module

## Purpose

This module provides a conservative appendix-level inference check for the baseline DID results.

## Input

Expected local input inside this module:

- `inputs/{CANONICAL_INPUT_NAME}`

For compatibility, if only the old file name `inputs/{LEGACY_INPUT_NAME}` exists, the script copies it to the canonical input name before processing.

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
"""
    (out_root / "README.md").write_text(readme, encoding="utf-8")


if __name__ == "__main__":
    main()
