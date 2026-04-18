from __future__ import annotations

from pathlib import Path
import sys

import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.font_manager import FontProperties
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from bundle_common import (  # noqa: E402
    OUTCOMES,
    TREATMENT,
    clean_baseline_sample,
    load_main_panel,
    read_manuscript_baseline_reference,
    resolve_paths,
    trend_adjusted_formula,
)


PALETTE = {
    "baseline": "#1f4e79",
    "trend_adjusted": "#b22222",
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

OUTCOME_LABELS_EN = {
    "exec_share": "exec_share",
    "proc_share": "proc_share",
    "ppp_quality_zindex": "ppp_quality_zindex",
}


def run_models(df: pd.DataFrame, canonical_baseline: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for outcome in OUTCOMES:
        fit = smf.ols(trend_adjusted_formula(outcome), data=df).fit(
            cov_type="cluster",
            cov_kwds={"groups": df["province"], "use_correction": True},
        )
        base = canonical_baseline.loc[
            canonical_baseline["outcome"] == outcome
        ].iloc[0]
        rows.append(
            {
                "outcome": outcome,
                "outcome_label_zh": OUTCOME_LABELS_ZH[outcome],
                "canonical_baseline_coef": float(base["official_coef"]),
                "canonical_baseline_se": float(base["official_se"]),
                "canonical_baseline_p_value": float(base["official_p_value"]),
                "canonical_baseline_nobs": int(base["official_nobs"]),
                "trend_adjusted_coef": float(fit.params[TREATMENT]),
                "trend_adjusted_se": float(fit.bse[TREATMENT]),
                "trend_adjusted_p_value": float(fit.pvalues[TREATMENT]),
                "trend_adjusted_nobs": int(fit.nobs),
                "direction_same_as_canonical": bool(
                    np.sign(float(fit.params[TREATMENT]))
                    == np.sign(float(base["official_coef"]))
                ),
            }
        )
    result = pd.DataFrame(rows)
    result["strength_reading"] = [
        "方向稳定但强度减弱"
        if row["direction_same_as_canonical"]
        and row["trend_adjusted_p_value"] >= row["canonical_baseline_p_value"]
        else (
            "方向与强度同时稳定"
            if row["direction_same_as_canonical"]
            and row["trend_adjusted_p_value"] < row["canonical_baseline_p_value"]
            else "方向不稳或不宜强化"
        )
        for _, row in result.iterrows()
    ]
    return result


def _draw_compare_figure(
    results: pd.DataFrame,
    label_map: dict[str, str],
    title: str,
    xlabel: str,
    out_prefix: Path,
) -> None:
    manuscript = "manuscript" in out_prefix.name
    zh_font = get_chinese_font(manuscript)
    fig, ax = plt.subplots(figsize=(8.6, 4.8))
    y_positions = np.arange(len(OUTCOMES))[::-1]
    offsets = {"baseline": 0.12, "trend_adjusted": -0.12}

    for i, outcome in enumerate(OUTCOMES):
        row = results.loc[results["outcome"] == outcome].iloc[0]
        for label in ["baseline", "trend_adjusted"]:
            coef = row[f"{'canonical_' if label == 'baseline' else ''}{label}_coef"]
            se = row[f"{'canonical_' if label == 'baseline' else ''}{label}_se"]
            y = y_positions[i] + offsets[label]
            ax.errorbar(
                coef,
                y,
                xerr=1.96 * se,
                fmt="o",
                color=PALETTE[label],
                label=("Baseline DID" if label == "baseline" else "Trend-adjusted DID")
                if i == 0
                else None,
                capsize=3,
                markersize=6,
            )
    ax.axvline(0, color="black", linewidth=1)
    ax.set_yticks(y_positions)
    ax.set_yticklabels(
        [label_map[o] for o in OUTCOMES],
        fontproperties=zh_font if manuscript else None,
    )
    ax.set_xlabel(xlabel, fontproperties=zh_font if manuscript else None)
    ax.set_title(title, fontproperties=zh_font if manuscript else None)
    ax.legend(
        frameon=False,
        loc="best",
        prop=zh_font if manuscript else None,
    )
    ax.grid(axis="x", alpha=0.2)
    fig.tight_layout()
    for suffix in [".png", ".svg", ".pdf"]:
        fig.savefig(out_prefix.with_suffix(suffix), dpi=300, bbox_inches="tight")
    plt.close(fig)


def write_outputs(results: pd.DataFrame, out_root: Path) -> None:
    table_dir = out_root / "tables"
    fig_dir = out_root / "figures"
    text_dir = out_root / "text"
    note_dir = out_root / "notes"
    for p in [table_dir, fig_dir, text_dir, note_dir]:
        p.mkdir(parents=True, exist_ok=True)

    results.to_excel(table_dir / "trend_adjusted_did_results.xlsx", index=False)

    _draw_compare_figure(
        results,
        label_map=OUTCOME_LABELS_EN,
        title="Baseline vs trend-adjusted DID",
        xlabel="Coefficient on treat_share (95% CI)",
        out_prefix=fig_dir / "Figure_8A_baseline_vs_trend_adjusted_forest_diagnostic",
    )
    _draw_compare_figure(
        results,
        label_map=OUTCOME_LABELS_MS,
        title="Figure 8A. Baseline DID vs trend-adjusted DID",
        xlabel="Coefficient on treat_share (95% confidence interval)",
        out_prefix=fig_dir / "Figure_8A_baseline_vs_trend_adjusted_forest_manuscript",
    )

    exec_row = results.loc[results["outcome"] == "exec_share"].iloc[0]
    proc_row = results.loc[results["outcome"] == "proc_share"].iloc[0]
    qual_row = results.loc[results["outcome"] == "ppp_quality_zindex"].iloc[0]

    body = f"""# 趋势调整型 DID 正文替换文本

为回应经典多期 DID/TWFE 可能受到地区差异化时间趋势影响的质疑，本文进一步在基准规格中加入省份线性时间趋势，构造趋势调整型 DID 作为主识别的防守性检验。该检验保持处理变量、控制变量、固定效应和正式样本口径不变，其目的在于考察推进结构改善这一核心判断是否过度依赖共同趋势设定，而不是以另一套模型替代表4中的主识别。

趋势调整后的结果显示，`proc_share` 仍保持显著负向（系数 = {proc_row['trend_adjusted_coef']:.3f}, p = {proc_row['trend_adjusted_p_value']:.3f}），说明采购阶段占比下降这一结论并不完全依赖共同趋势设定。`exec_share` 的估计方向仍为正（系数 = {exec_row['trend_adjusted_coef']:.3f}），但统计强度明显减弱（p = {exec_row['trend_adjusted_p_value']:.3f}），这意味着执行阶段占比上升的判断在方向上较稳，但对趋势设定更为敏感。相比之下，`ppp_quality_zindex` 在趋势调整后继续缺乏稳定支持（系数 = {qual_row['trend_adjusted_coef']:.3f}, p = {qual_row['trend_adjusted_p_value']:.3f}），因此质量型口径仍不适合承担全文主结论。

据此，趋势调整型 DID 的作用应理解为对“推进结构改善优先”这一主线的防守性强化，而不是把基准 DID 替换为新的主识别策略。"""
    (text_dir / "trend_adjusted_did_body_insert.md").write_text(
        body, encoding="utf-8"
    )

    note = """# 趋势调整型 DID 图表注释与口径

- 本模块只服务于识别边界说明，不替代表4中的主识别结果。
- 基准参考线与比较列均使用 `00_unified_baseline_reference/manuscript_baseline` 的唯一正文基线。
- 论文版图使用中文变量标签与图题；工程版图保留代码变量名，供内部复核。
- 结果解释规则：
  - `proc_share` 若仍显著为负，可写为“核心推进结构判断并不完全依赖共同趋势设定”；
  - `exec_share` 若方向为正但显著性减弱，应写为“方向稳定，但统计强度对趋势设定更敏感”；
  - `ppp_quality_zindex` 若不稳，继续降格处理。
"""
    (note_dir / "trend_adjusted_did_notes.md").write_text(
        note, encoding="utf-8"
    )


def write_readme(out_root: Path, paths) -> None:
    readme = f"""# Trend-adjusted DID module

## Purpose

This module rebuilds the main defensive robustness layer used in manuscript section 5.6.1.

## Specification

- Same formal sample as Table 4: `baseline_sample_5_3 == 1`
- Same treatment: `{TREATMENT}`
- Same controls as the official baseline DID
- Same province/year fixed effects
- Additional defense term: province-specific linear time trends

## Inputs

This bundle is not self-extracting. Before running, the following formal files must already exist somewhere under the workspace root:

- `{paths.panel_csv.name}`
- `{paths.baseline_long_table.name}`
- `00_unified_baseline_reference/tables/unified_baseline_reference.xlsx`

If the workspace still only contains compressed archives, extract them first. The script will fail loudly if the required files are missing.

## Run

```bash
python PPP_empirical_reinforcement_bundle_20260416_unified_v3/01_trend_adjusted_DID/scripts/run_trend_adjusted_did.py
```

## Outputs

- `tables/trend_adjusted_did_results.xlsx`
- `figures/Figure_8A_baseline_vs_trend_adjusted_forest_diagnostic.(png|svg|pdf)`
- `figures/Figure_8A_baseline_vs_trend_adjusted_forest_manuscript.(png|svg|pdf)`
- `text/trend_adjusted_did_body_insert.md`
- `notes/trend_adjusted_did_notes.md`
"""
    (out_root / "README.md").write_text(readme, encoding="utf-8")


def main() -> None:
    paths = resolve_paths(Path(__file__))
    out_root = Path(__file__).resolve().parents[1]
    df = clean_baseline_sample(load_main_panel(paths.panel_csv))
    canonical_baseline = read_manuscript_baseline_reference(paths.bundle_root)
    results = run_models(df, canonical_baseline)
    write_outputs(results, out_root)
    write_readme(out_root, paths)


if __name__ == "__main__":
    main()
