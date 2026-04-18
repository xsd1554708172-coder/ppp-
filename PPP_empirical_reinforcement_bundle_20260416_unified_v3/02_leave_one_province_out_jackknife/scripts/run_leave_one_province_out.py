from __future__ import annotations

from pathlib import Path
import sys

import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.font_manager import FontProperties
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
    read_manuscript_baseline_reference,
    resolve_paths,
)


DISPLAY_ORDER = ["exec_share", "proc_share", "ppp_quality_zindex"]
OUTCOME_LABELS_ZH = {
    "exec_share": "执行阶段占比",
    "proc_share": "采购阶段占比",
    "ppp_quality_zindex": "综合治理质量指数",
}
OUTCOME_LABELS_MS = {
    "exec_share": "Execution-stage share",
    "proc_share": "Procurement-stage share",
    "ppp_quality_zindex": "Governance quality index",
}
COLORS = {
    "exec_share": "#1f4e79",
    "proc_share": "#b22222",
}


def get_chinese_font(manuscript: bool) -> FontProperties | None:
    if not manuscript:
        return None
    candidates = ["Microsoft YaHei", "SimHei", "SimSun", "Noto Sans CJK SC"]
    installed = {f.name for f in font_manager.fontManager.ttflist}
    for name in candidates:
        if name in installed:
            plt.rcParams["axes.unicode_minus"] = False
            return FontProperties(fname=font_manager.findfont(name, fallback_to_default=False))
    return None


def run_leave_one_out(
    df: pd.DataFrame, canonical_baseline: pd.DataFrame
) -> tuple[pd.DataFrame, pd.DataFrame]:
    province_order = sorted(df["province"].unique().tolist())
    per_rows = []
    summary_rows = []

    for outcome in OUTCOMES:
        canonical_row = canonical_baseline.loc[
            canonical_baseline["outcome"] == outcome
        ].iloc[0]
        baseline_coef = float(canonical_row["official_coef"])
        baseline_se = float(canonical_row["official_se"])
        baseline_p = float(canonical_row["official_p_value"])
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
                    "outcome_label_zh": OUTCOME_LABELS_ZH[outcome],
                    "province_excluded": province,
                    "nobs": int(fit.nobs),
                    "coef": coef,
                    "se": float(fit.bse[TREATMENT]),
                    "p_value": pval,
                    "delta_vs_canonical_baseline": delta,
                    "abs_delta_vs_canonical_baseline": abs(delta),
                    "sign_flip_vs_canonical_baseline": bool(
                        np.sign(coef) != np.sign(baseline_coef)
                    ),
                    "sig_jump_5pct_vs_canonical_baseline": bool(
                        (pval < 0.05) != (baseline_p < 0.05)
                    ),
                }
            )

        per_df = pd.DataFrame(deletion_rows)
        per_rows.append(per_df)

        worst_idx = per_df["abs_delta_vs_canonical_baseline"].idxmax()
        summary_rows.append(
            {
                "outcome": outcome,
                "outcome_label_zh": OUTCOME_LABELS_ZH[outcome],
                "canonical_baseline_coef": baseline_coef,
                "canonical_baseline_se": baseline_se,
                "canonical_baseline_p_value": baseline_p,
                "min_coef": float(per_df["coef"].min()),
                "max_coef": float(per_df["coef"].max()),
                "n_sign_flip_vs_canonical_baseline": int(
                    per_df["sign_flip_vs_canonical_baseline"].sum()
                ),
                "n_sig_jump_5pct_vs_canonical_baseline": int(
                    per_df["sig_jump_5pct_vs_canonical_baseline"].sum()
                ),
                "max_abs_deviation_province": str(
                    per_df.loc[worst_idx, "province_excluded"]
                ),
                "max_abs_deviation": float(
                    per_df.loc[worst_idx, "abs_delta_vs_canonical_baseline"]
                ),
            }
        )

    return pd.concat(per_rows, ignore_index=True), pd.DataFrame(summary_rows)


def _draw_figure(
    per_df: pd.DataFrame,
    summary_df: pd.DataFrame,
    out_prefix: Path,
    manuscript: bool,
) -> None:
    zh_font = get_chinese_font(manuscript)
    fig, axes = plt.subplots(2, 1, figsize=(10, 7.5), sharex=False)
    outcomes = ["exec_share", "proc_share"]

    for ax, outcome in zip(axes, outcomes):
        sub = per_df.loc[per_df["outcome"] == outcome].copy()
        sub = sub.sort_values("coef").reset_index(drop=True)
        x = np.arange(len(sub))
        baseline = float(
            summary_df.loc[
                summary_df["outcome"] == outcome, "canonical_baseline_coef"
            ].iloc[0]
        )
        ax.scatter(x, sub["coef"], color=COLORS[outcome], s=22, alpha=0.9)
        ax.axhline(baseline, color="black", linestyle="--", linewidth=1)
        if manuscript:
            ax.set_title(
                f"{OUTCOME_LABELS_MS[outcome]}: leave-one-province-out stability",
                fontproperties=zh_font,
            )
            ax.set_ylabel("Coefficient on treat_share", fontproperties=zh_font)
        else:
            ax.set_title(f"{outcome}: leave-one-province-out stability")
            ax.set_ylabel("coef on treat_share")
        ax.grid(axis="y", alpha=0.2)
        ax.set_xticks([0, len(sub) // 2, len(sub) - 1])
        ax.set_xticklabels(["min", "mid", "max"])

    axes[-1].set_xlabel(
        "Deletion rank after removing one province"
        if manuscript
        else "province deletion rank",
        fontproperties=zh_font if manuscript else None,
    )
    fig.tight_layout()
    for suffix in [".png", ".svg", ".pdf"]:
        fig.savefig(out_prefix.with_suffix(suffix), dpi=300, bbox_inches="tight")
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

    _draw_figure(
        per_df,
        summary_df,
        fig_dir / "Figure_8B_leave_one_province_out_stability_diagnostic",
        manuscript=False,
    )
    _draw_figure(
        per_df,
        summary_df,
        fig_dir / "Figure_8B_leave_one_province_out_stability_manuscript",
        manuscript=True,
    )

    exec_row = summary_df.loc[summary_df["outcome"] == "exec_share"].iloc[0]
    proc_row = summary_df.loc[summary_df["outcome"] == "proc_share"].iloc[0]
    qual_row = summary_df.loc[summary_df["outcome"] == "ppp_quality_zindex"].iloc[0]

    body = f"""# Leave-one-province-out 正文替换文本

为检验基准 DID 结果是否主要由单一地区驱动，本文进一步实施 leave-one-province-out / jackknife 诊断：在保持处理变量、控制变量、固定效应与聚类口径不变的前提下，依次剔除一个省份并重复估计表4的基准 DID。结果显示，`exec_share` 与 `proc_share` 在逐省剔除后均未出现方向翻转，说明推进结构改善这一核心判断并非由单一省份完全驱动。

与此同时，该检验也表明统计强度并非完全不受样本构成影响。对 `exec_share` 和 `proc_share` 而言，删去个别地区后显著性会出现变化，其中最大偏离分别来自 `{exec_row['max_abs_deviation_province']}` 与 `{proc_row['max_abs_deviation_province']}`。据此，更稳妥的表述应是：方向判断较稳，但统计强度对个别地区具有一定敏感性。相比之下，`ppp_quality_zindex` 在逐省剔除后继续表现为幅度波动较大、统计支持不足，因此仍不适合承担全文主结论。

这项检验回答的是“主结果是否被单一地区完全驱动”，而不是把基准 DID 包装成完全不受样本构成影响的强稳健结论。"""
    (text_dir / "leave_one_province_out_body_insert.md").write_text(
        body, encoding="utf-8"
    )

    notes = f"""# Leave-one-province-out 图表注释与口径

- 本模块的基准参考线统一使用 `00_unified_baseline_reference/manuscript_baseline` 的唯一正文基线。
- 论文版图用于正文 Figure 8B；工程版图保留英文变量名，供内部诊断。
- 结果阅读规则：
  - `exec_share`：sign flip = {int(exec_row['n_sign_flip_vs_canonical_baseline'])}，显著性状态变化 = {int(exec_row['n_sig_jump_5pct_vs_canonical_baseline'])}；
  - `proc_share`：sign flip = {int(proc_row['n_sign_flip_vs_canonical_baseline'])}，显著性状态变化 = {int(proc_row['n_sig_jump_5pct_vs_canonical_baseline'])}；
  - `ppp_quality_zindex`：继续只保留为边界说明。
- 正文宜写成“方向稳定，但统计强度对个别地区具有一定敏感性”，不宜写成“完全稳健”。
"""
    (note_dir / "leave_one_province_out_notes.md").write_text(
        notes, encoding="utf-8"
    )


def write_readme(out_root: Path, paths) -> None:
    readme = f"""# Leave-one-province-out / jackknife module

## Purpose

This module answers a narrow robustness question: whether the core structural results are entirely driven by any single province.

## Inputs

The following files must already exist somewhere under the workspace root:

- `{paths.panel_csv.name}`
- `00_unified_baseline_reference/tables/unified_baseline_reference.xlsx`

If the workspace still only contains compressed archives, extract them first. The script will fail loudly if the required files are missing.

## Run

```bash
python PPP_empirical_reinforcement_bundle_20260416_unified_v3/02_leave_one_province_out_jackknife/scripts/run_leave_one_province_out.py
```

## Outputs

- `tables/leave_one_province_out_results.xlsx`
- `tables/leave_one_province_out_stability_summary.xlsx`
- `figures/Figure_8B_leave_one_province_out_stability_diagnostic.(png|svg|pdf)`
- `figures/Figure_8B_leave_one_province_out_stability_manuscript.(png|svg|pdf)`
- `text/leave_one_province_out_body_insert.md`
- `notes/leave_one_province_out_notes.md`

## Reading boundary

This is an auxiliary diagnostic layer. It supports sign stability and sample-sensitivity discussion; it does not replace the baseline DID.
"""
    (out_root / "README.md").write_text(readme, encoding="utf-8")


def main() -> None:
    paths = resolve_paths(Path(__file__))
    out_root = Path(__file__).resolve().parents[1]
    df = clean_baseline_sample(load_main_panel(paths.panel_csv))
    canonical_baseline = read_manuscript_baseline_reference(paths.bundle_root)
    per_df, summary_df = run_leave_one_out(df, canonical_baseline)
    write_outputs(per_df, summary_df, out_root)
    write_readme(out_root, paths)


if __name__ == "__main__":
    main()
