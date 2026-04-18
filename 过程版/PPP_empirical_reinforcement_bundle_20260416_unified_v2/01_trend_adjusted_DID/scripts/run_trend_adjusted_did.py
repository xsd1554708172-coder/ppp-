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
    clean_baseline_sample,
    fit_clustered,
    load_main_panel,
    read_official_baseline_rows,
    resolve_paths,
    trend_adjusted_formula,
)


PALETTE = {
    "baseline": "#1f77b4",
    "trend_adjusted": "#d62728",
}


def run_models(df: pd.DataFrame, official_baseline: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for outcome in OUTCOMES:
        fit = fit_clustered(df, trend_adjusted_formula(outcome))
        base = official_baseline.loc[official_baseline["outcome"] == outcome].iloc[0]
        rows.append(
            {
                "outcome": outcome,
                "baseline_coef": float(base["official_coef"]),
                "baseline_se": float(base["official_se"]),
                "baseline_p_value": float(base["official_p_value"]),
                "trend_adjusted_coef": float(fit.params[TREATMENT]),
                "trend_adjusted_se": float(fit.bse[TREATMENT]),
                "trend_adjusted_p_value": float(fit.pvalues[TREATMENT]),
                "nobs": int(fit.nobs),
                "direction_same_as_baseline": bool(
                    np.sign(float(fit.params[TREATMENT])) == np.sign(float(base["official_coef"]))
                ),
            }
        )
    return pd.DataFrame(rows)


def draw_figure(results: pd.DataFrame, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    y_positions = np.arange(len(OUTCOMES))[::-1]
    offsets = {"baseline": 0.12, "trend_adjusted": -0.12}

    for i, outcome in enumerate(OUTCOMES):
        row = results.loc[results["outcome"] == outcome].iloc[0]
        for label in ["baseline", "trend_adjusted"]:
            coef = row[f"{label}_coef"]
            se = row[f"{label}_se"]
            y = y_positions[i] + offsets[label]
            ax.errorbar(
                coef,
                y,
                xerr=1.96 * se,
                fmt="o",
                color=PALETTE[label],
                label=label if i == 0 else None,
                capsize=3,
            )
    ax.axvline(0, color="black", linewidth=1)
    ax.set_yticks(y_positions)
    ax.set_yticklabels(OUTCOMES)
    ax.set_xlabel("Coefficient on treat_share (95% CI)")
    ax.set_title("Baseline vs trend-adjusted DID")
    ax.legend(frameon=False, loc="best")
    ax.grid(axis="x", alpha=0.2)
    fig.tight_layout()
    fig.savefig(path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def write_outputs(results: pd.DataFrame, out_root: Path) -> None:
    table_dir = out_root / "tables"
    fig_dir = out_root / "figures"
    text_dir = out_root / "text"
    note_dir = out_root / "notes"
    for p in [table_dir, fig_dir, text_dir, note_dir]:
        p.mkdir(parents=True, exist_ok=True)

    results.to_excel(table_dir / "trend_adjusted_did_results.xlsx", index=False)
    draw_figure(results, fig_dir / "Figure_8A_baseline_vs_trend_adjusted_forest.png")

    exec_row = results.loc[results["outcome"] == "exec_share"].iloc[0]
    proc_row = results.loc[results["outcome"] == "proc_share"].iloc[0]
    qual_row = results.loc[results["outcome"] == "ppp_quality_zindex"].iloc[0]

    body = f"""# Trend-adjusted DID body insert

为回应经典多期 DID/TWFE 可能受到省份既有差异化趋势影响的质疑，本文进一步在基准规格中加入省份线性时间趋势，构造趋势调整型 DID 作为主识别的防守性检验。该检验并不替代表4中的基准 DID，而是围绕同一处理变量 `{TREATMENT}`、同一控制变量体系以及同一正式样本口径，检验推进结构结论是否过度依赖共同趋势设定。

结果表明，`proc_share` 在趋势调整后仍保持显著负向（系数 = {proc_row['trend_adjusted_coef']:.3f}, p = {proc_row['trend_adjusted_p_value']:.3f}），说明采购阶段占比下降这一判断并不完全依赖于共同趋势假设。`exec_share` 的估计方向依然为正（系数 = {exec_row['trend_adjusted_coef']:.3f}），但统计强度明显减弱（p = {exec_row['trend_adjusted_p_value']:.3f}），这意味着执行阶段占比上升的结论在方向上较稳，但对趋势设定更为敏感。相比之下，`ppp_quality_zindex` 在趋势调整后不再维持基准回归中的正向估计，且统计上继续不显著（系数 = {qual_row['trend_adjusted_coef']:.3f}, p = {qual_row['trend_adjusted_p_value']:.3f}），因此质量型口径更不能承担全文主结论。

据此，趋势调整 DID 的主要作用是加强对“推进结构改善优先”这一核心判断的防守，而不是把它写成新的主识别策略或将基准 DID 的所有结果一并强化为同等稳健的结论。
"""
    (text_dir / "trend_adjusted_did_body_insert.md").write_text(body, encoding="utf-8")

    note = f"""# Trend-adjusted DID notes

## Model

- Same sample as table 4: baseline_sample_5_3 == 1
- Same treatment: `{TREATMENT}`
- Same controls: dfi, digital_econ, ln_rd_expenditure, ln_tech_contract_value, ln_patent_grants
- Same fixed effects: province FE + year FE
- Additional defense term: province-specific linear trends

## Reading rule

- `proc_share` remains the cleanest defensive result.
- `exec_share` remains directionally aligned but becomes more sensitive once province-specific trends are absorbed.
- `ppp_quality_zindex` remains too unstable for any headline claim.

This module is a defensive robustness layer, not a replacement main model.
"""
    (note_dir / "trend_adjusted_did_notes.md").write_text(note, encoding="utf-8")


def write_readme(out_root: Path) -> None:
    readme = """# Trend-adjusted DID module

Run from the workspace root:

```bash
python PPP_empirical_reinforcement_bundle_20260416_unified_v2/01_trend_adjusted_DID/scripts/run_trend_adjusted_did.py
```

This module reruns the official baseline DID sample and adds province-specific linear trends:

```text
outcome ~ treat_share + controls + C(province) + C(year) + C(province):year_idx
```

Outputs:
- `tables/trend_adjusted_did_results.xlsx`
- `figures/Figure_8A_baseline_vs_trend_adjusted_forest.png`
- `text/trend_adjusted_did_body_insert.md`
- `notes/trend_adjusted_did_notes.md`
"""
    (out_root / "scripts" / "README.md").write_text(readme, encoding="utf-8")


def main() -> None:
    paths = resolve_paths(Path(__file__))
    out_root = Path(__file__).resolve().parents[1]
    df = clean_baseline_sample(load_main_panel(paths.panel_csv))
    official_baseline = read_official_baseline_rows(paths.baseline_long_table)
    results = run_models(df, official_baseline)
    write_outputs(results, out_root)
    write_readme(out_root)


if __name__ == "__main__":
    main()
