from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from bundle_common import read_official_baseline_rows, resolve_paths  # noqa: E402


def main() -> None:
    paths = resolve_paths(Path(__file__))
    out_root = Path(__file__).resolve().parents[1]
    table_dir = out_root / "tables"
    note_dir = out_root / "notes"
    text_dir = out_root / "text"
    input_dir = out_root / "inputs"
    for p in [table_dir, note_dir, text_dir, input_dir]:
        p.mkdir(parents=True, exist_ok=True)

    src = input_dir / "baseline_did_bootstrap_or_permutation_pvalues.xlsx"
    if not src.exists():
        raise FileNotFoundError(
            "Bootstrap source table not found inside unified bundle inputs: "
            f"{src}"
        )

    summary = pd.read_excel(src, sheet_name="paper_ready_summary")
    official = read_official_baseline_rows(paths.baseline_long_table)
    summary = summary.merge(
        official[["outcome", "official_coef", "official_se", "official_p_value", "official_nobs"]],
        on="outcome",
        how="left",
    )
    summary["canonical_baseline_coef"] = summary["official_coef"]
    summary["canonical_baseline_p_value"] = summary["official_p_value"]
    summary["module_role"] = "appendix_level_support"
    summary["reading_rule"] = [
        "Direction stable; significance more sensitive under conservative inference"
        for _ in range(len(summary))
    ]
    summary.to_excel(table_dir / "small_sample_inference_summary.xlsx", index=False)

    note = """# Small-sample / wild cluster bootstrap notes

This layer is intentionally downgraded. Its purpose is not to replace the baseline DID or the trend-adjusted defense. It only answers a narrower question: whether the baseline significance becomes materially more fragile under more conservative small-sample inference.

Current reading rule:
- keep this as appendix-level support or a very short paragraph in section 5.6.3;
- stress direction stability for the core structural outcomes;
- stress greater sensitivity in statistical strength;
- do not use it to strengthen quality-type claims.
"""
    (note_dir / "small_sample_inference_notes.md").write_text(note, encoding="utf-8")

    exec_row = summary.loc[summary["outcome"] == "exec_share"].iloc[0]
    proc_row = summary.loc[summary["outcome"] == "proc_share"].iloc[0]
    qual_row = summary.loc[summary["outcome"] == "ppp_quality_zindex"].iloc[0]
    body = f"""# Small-sample inference body insert

在更保守的小样本推断框架下，`exec_share` 与 `proc_share` 的方向仍与基准 DID 保持一致，但 bootstrap p 值分别为 {exec_row['wild_bootstrap_p']:.3f} 和 {proc_row['wild_bootstrap_p']:.3f}，说明推进结构结果在更保守推断下仍具有方向稳定性，但统计强度更为敏感。相比之下，`ppp_quality_zindex` 的 bootstrap p 值为 {qual_row['wild_bootstrap_p']:.3f}，继续不支持将质量型口径写成稳定主结论。由此，这一层检验更适合作为边界说明，而不应与正文主识别或趋势调整型防守检验处于同一层级。
"""
    (text_dir / "bootstrap_body_insert.md").write_text(body, encoding="utf-8")

    readme = """# Small-sample inference summary module

Run from the workspace root:

```bash
python PPP_empirical_reinforcement_bundle_20260416_unified_v2/03_small_sample_inference_wild_cluster_bootstrap/scripts/summarize_small_sample_inference.py
```

This script reads the existing clean bootstrap summary, standardizes filenames and wording, and produces appendix-level support files for manuscript integration.

Expected local input:

- `../inputs/baseline_did_bootstrap_or_permutation_pvalues.xlsx`
"""
    (out_root / "scripts" / "README.md").write_text(readme, encoding="utf-8")


if __name__ == "__main__":
    main()
