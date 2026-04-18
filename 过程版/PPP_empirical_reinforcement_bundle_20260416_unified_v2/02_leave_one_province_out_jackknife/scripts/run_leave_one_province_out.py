from __future__ import annotations

from pathlib import Path
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from bundle_common import (  # noqa: E402
    OUTCOMES,
    TREATMENT,
    baseline_formula,
    clean_baseline_sample,
    fit_clustered,
    load_main_panel,
    read_official_baseline_rows,
    resolve_paths,
)


DISPLAY_ORDER = ["exec_share", "proc_share", "ppp_quality_zindex"]


def run_leave_one_out(
    df: pd.DataFrame, official_baseline: pd.DataFrame
) -> tuple[pd.DataFrame, pd.DataFrame]:
    province_order = sorted(df["province"].unique().tolist())
    per_rows = []
    summary_rows = []

    for outcome in OUTCOMES:
        full_fit = fit_clustered(df, baseline_formula(outcome))
        baseline_coef = float(full_fit.params[TREATMENT])
        baseline_se = float(full_fit.bse[TREATMENT])
        baseline_p = float(full_fit.pvalues[TREATMENT])
        deletion_rows = []

        for province in province_order:
            reduced = df.loc[df["province"] != province].copy()
            fit = fit_clustered(reduced, baseline_formula(outcome))
            coef = float(fit.params[TREATMENT])
            pval = float(fit.pvalues[TREATMENT])
            delta = coef - baseline_coef
            deletion_rows.append(
                {
                    "outcome": outcome,
                    "province_excluded": province,
                    "nobs": int(fit.nobs),
                    "coef": coef,
                    "se": float(fit.bse[TREATMENT]),
                    "p_value": pval,
                    "delta_vs_baseline": delta,
                    "abs_delta_vs_baseline": abs(delta),
                    "sign_flip": bool(np.sign(coef) != np.sign(baseline_coef)),
                    "sig_jump_5pct": bool((pval < 0.05) != (baseline_p < 0.05)),
                }
            )

        per_df = pd.DataFrame(deletion_rows)
        per_rows.append(per_df)

        worst_idx = per_df["abs_delta_vs_baseline"].idxmax()
        summary_rows.append(
            {
                "outcome": outcome,
                "module_fullsample_coef": baseline_coef,
                "module_fullsample_se": baseline_se,
                "module_fullsample_p_value": baseline_p,
                "canonical_baseline_coef": float(
                    official_baseline.loc[official_baseline["outcome"] == outcome, "official_coef"].iloc[0]
                ),
                "canonical_baseline_se": float(
                    official_baseline.loc[official_baseline["outcome"] == outcome, "official_se"].iloc[0]
                ),
                "canonical_baseline_p_value": float(
                    official_baseline.loc[official_baseline["outcome"] == outcome, "official_p_value"].iloc[0]
                ),
                "min_coef": float(per_df["coef"].min()),
                "max_coef": float(per_df["coef"].max()),
                "n_sign_flip": int(per_df["sign_flip"].sum()),
                "n_sig_jump_5pct": int(per_df["sig_jump_5pct"].sum()),
                "max_abs_deviation_province": str(
                    per_df.loc[worst_idx, "province_excluded"]
                ),
                "max_abs_deviation": float(per_df.loc[worst_idx, "abs_delta_vs_baseline"]),
            }
        )

    return pd.concat(per_rows, ignore_index=True), pd.DataFrame(summary_rows)


def draw_figure(per_df: pd.DataFrame, summary_df: pd.DataFrame, out_path: Path) -> None:
    fig, axes = plt.subplots(2, 1, figsize=(10, 7.5), sharex=False)
    outcomes = ["exec_share", "proc_share"]
    colors = {"exec_share": "#1f77b4", "proc_share": "#d62728"}

    for ax, outcome in zip(axes, outcomes):
        sub = per_df.loc[per_df["outcome"] == outcome].copy()
        sub = sub.sort_values("coef").reset_index(drop=True)
        x = np.arange(len(sub))
        baseline = float(
            summary_df.loc[summary_df["outcome"] == outcome, "module_fullsample_coef"].iloc[0]
        )
        ax.scatter(x, sub["coef"], color=colors[outcome], s=22, alpha=0.9)
        ax.axhline(baseline, color="black", linestyle="--", linewidth=1)
        ax.set_title(f"{outcome}: leave-one-province-out stability")
        ax.set_ylabel("coef on treat_share")
        ax.grid(axis="y", alpha=0.2)
        worst_row = sub.loc[sub["abs_delta_vs_baseline"].idxmax()]
        ax.annotate(
            "largest deviation",
            xy=(worst_row.name, worst_row["coef"]),
            xytext=(8, 6),
            textcoords="offset points",
            fontsize=8,
        )
        ax.set_xticks([0, len(sub)//2, len(sub)-1])
        ax.set_xticklabels(["min", "mid", "max"])

    axes[-1].set_xlabel("province deletion rank (sorted by coefficient)")
    fig.tight_layout()
    fig.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def write_outputs(per_df: pd.DataFrame, summary_df: pd.DataFrame, out_root: Path) -> None:
    table_dir = out_root / "tables"
    fig_dir = out_root / "figures"
    text_dir = out_root / "text"
    note_dir = out_root / "notes"
    for p in [table_dir, fig_dir, text_dir, note_dir]:
        p.mkdir(parents=True, exist_ok=True)

    with pd.ExcelWriter(table_dir / "leave_one_province_out_results.xlsx", engine="openpyxl") as writer:
        per_df.to_excel(writer, index=False, sheet_name="per_province")
        summary_df.to_excel(writer, index=False, sheet_name="summary")
    summary_df.to_excel(
        table_dir / "leave_one_province_out_stability_summary.xlsx",
        index=False,
    )
    draw_figure(
        per_df,
        summary_df,
        fig_dir / "Figure_8B_leave_one_province_out_stability.png",
    )

    exec_row = summary_df.loc[summary_df["outcome"] == "exec_share"].iloc[0]
    proc_row = summary_df.loc[summary_df["outcome"] == "proc_share"].iloc[0]
    qual_row = summary_df.loc[summary_df["outcome"] == "ppp_quality_zindex"].iloc[0]

    body = f"""# Leave-one-province-out body insert

为检验基准 DID 结果是否主要由单一地区驱动，本文进一步实施 leave-one-province-out / jackknife 诊断：在保持处理变量、控制变量、固定效应与聚类标准误口径不变的前提下，依次剔除一个省份并重复估计基准 DID。结果显示，`exec_share` 与 `proc_share` 在删除任一省份后均未出现方向翻转，说明推进结构改善这一核心判断并非由单一省份机械驱动。与此同时，`{exec_row['max_abs_deviation_province']}` 对 `exec_share` 的系数幅度影响最大，`{proc_row['max_abs_deviation_province']}` 对 `proc_share` 的系数幅度影响最大，相关显著性均出现明显减弱。这意味着主结论在方向上较稳，但统计强度对个别地区仍具有一定敏感性。

相比之下，`ppp_quality_zindex` 在 leave-one-province-out 下继续表现出幅度波动较大、统计支持不足的特征，因此更不适合承担全文主结论。由此看，这一检验回答的是“主结果是否被单一省份完全驱动”，而不是把基准 DID 重新包装为完全不受样本构成影响的强稳健结论。
"""
    (text_dir / "leave_one_province_out_body_insert.md").write_text(body, encoding="utf-8")

    notes = f"""# Leave-one-province-out notes

- `exec_share`: sign flips = {int(exec_row['n_sign_flip'])}; significance-status changes = {int(exec_row['n_sig_jump_5pct'])}; largest deviation from `{exec_row['max_abs_deviation_province']}`.
- `proc_share`: sign flips = {int(proc_row['n_sign_flip'])}; significance-status changes = {int(proc_row['n_sig_jump_5pct'])}; largest deviation from `{proc_row['max_abs_deviation_province']}`.
- `ppp_quality_zindex`: sign flips = {int(qual_row['n_sign_flip'])}; significance-status changes = {int(qual_row['n_sig_jump_5pct'])}; unstable enough to remain appendix-level support only.

Interpretation boundary: this module is a sample-driven-risk diagnostic. It supports sign stability, not a claim of complete robustness.
"""
    (note_dir / "leave_one_province_out_notes.md").write_text(notes, encoding="utf-8")


def write_readme(out_root: Path) -> None:
    readme = """# Leave-one-province-out / jackknife module

Run from the workspace root:

```bash
python PPP_empirical_reinforcement_bundle_20260416_unified_v2/02_leave_one_province_out_jackknife/scripts/run_leave_one_province_out.py
```

This module keeps the official baseline DID specification fixed and repeatedly removes one province at a time.

Outputs:
- `tables/leave_one_province_out_results.xlsx`
- `tables/leave_one_province_out_stability_summary.xlsx`
- `figures/Figure_8B_leave_one_province_out_stability.png`
- `text/leave_one_province_out_body_insert.md`
- `notes/leave_one_province_out_notes.md`
"""
    (out_root / "scripts" / "README.md").write_text(readme, encoding="utf-8")


def main() -> None:
    paths = resolve_paths(Path(__file__))
    out_root = Path(__file__).resolve().parents[1]
    df = clean_baseline_sample(load_main_panel(paths.panel_csv))
    official_baseline = read_official_baseline_rows(paths.baseline_long_table)
    per_df, summary_df = run_leave_one_out(df, official_baseline)
    write_outputs(per_df, summary_df, out_root)
    write_readme(out_root)


if __name__ == "__main__":
    main()
