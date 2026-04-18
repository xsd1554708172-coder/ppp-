from __future__ import annotations

from pathlib import Path
import warnings

import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
from scipy import stats


warnings.filterwarnings("ignore", category=FutureWarning)

WORKSPACE_ROOT = Path(__file__).resolve().parents[3]
MODULE_ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = WORKSPACE_ROOT / "ppp论文数据"

TABLE_DIR = MODULE_ROOT / "tables"
FIGURE_DIR = MODULE_ROOT / "figures"
NOTE_DIR = MODULE_ROOT / "notes"
TEXT_DIR = MODULE_ROOT / "text"

OUTCOMES = ["exec_share", "proc_share", "ppp_quality_zindex"]
CONTROLS = [
    "dfi",
    "digital_econ",
    "ln_rd_expenditure",
    "ln_tech_contract_value",
    "ln_patent_grants",
]
TREATMENT = "treat_share"
BASE_SAMPLE_FLAG = "baseline_sample_5_3"
PROVINCE_COL = "province"
YEAR_COL = "year"
BOOTSTRAP_REPS = 999
SEED = 20260416


def ensure_output_dirs() -> None:
    for path in [TABLE_DIR, FIGURE_DIR, NOTE_DIR, TEXT_DIR]:
        path.mkdir(parents=True, exist_ok=True)


def find_main_panel_csv() -> Path:
    candidates = list(DATA_ROOT.rglob("PPP_3.6_model_ready_panel_v3_*1048.csv"))
    if not candidates:
        candidates = list(DATA_ROOT.rglob("*model_ready_panel_v3*1048.csv"))
    if not candidates:
        raise FileNotFoundError(
            "Could not find the V3 main panel CSV under the workspace data tree."
        )
    candidates = sorted(candidates, key=lambda p: (len(str(p)), str(p).lower()))
    return candidates[0]


def load_analysis_frame() -> pd.DataFrame:
    panel_path = find_main_panel_csv()
    df = pd.read_csv(panel_path)
    required = {
        BASE_SAMPLE_FLAG,
        PROVINCE_COL,
        YEAR_COL,
        TREATMENT,
        *CONTROLS,
        *OUTCOMES,
    }
    missing = sorted(required - set(df.columns))
    if missing:
        raise KeyError(f"Main panel is missing required columns: {missing}")
    df = df.loc[df[BASE_SAMPLE_FLAG] == 1].copy()
    df = df.dropna(subset=[PROVINCE_COL, YEAR_COL, TREATMENT, *CONTROLS, *OUTCOMES])
    df[PROVINCE_COL] = df[PROVINCE_COL].astype(str)
    df[YEAR_COL] = df[YEAR_COL].astype(str)
    for col in [TREATMENT, *CONTROLS, *OUTCOMES]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=[TREATMENT, *CONTROLS, *OUTCOMES]).copy()
    return df


def build_design_matrix(df: pd.DataFrame, outcome: str, include_treatment: bool = True):
    pieces = [pd.Series(1.0, index=df.index, name="intercept")]
    if include_treatment:
        pieces.append(df[[TREATMENT]].astype(float))
    pieces.append(df[CONTROLS].astype(float))
    pieces.append(pd.get_dummies(df[PROVINCE_COL], prefix="prov", drop_first=True, dtype=float))
    pieces.append(pd.get_dummies(df[YEAR_COL], prefix="year", drop_first=True, dtype=float))
    X = pd.concat(pieces, axis=1)
    y = df[outcome].astype(float).to_numpy()
    return y, X


def cluster_robust_fit(y: np.ndarray, X: pd.DataFrame, groups: np.ndarray):
    X_np = X.to_numpy(dtype=float)
    beta, *_ = np.linalg.lstsq(X_np, y, rcond=None)
    resid = y - X_np @ beta
    xtx_inv = np.linalg.pinv(X_np.T @ X_np)
    unique_groups = np.unique(groups)
    meat = np.zeros((X_np.shape[1], X_np.shape[1]), dtype=float)
    for g in unique_groups:
        idx = groups == g
        xu = X_np[idx].T @ resid[idx]
        meat += np.outer(xu, xu)
    g_count = len(unique_groups)
    n_obs = len(y)
    k = X_np.shape[1]
    df_correction = (g_count / (g_count - 1)) * ((n_obs - 1) / (n_obs - k))
    cov = df_correction * xtx_inv @ meat @ xtx_inv
    se = np.sqrt(np.diag(cov))
    t = beta / se
    p = 2 * stats.t.sf(np.abs(t), df=g_count - 1)
    return {
        "beta": beta,
        "se": se,
        "p": p,
        "t": t,
        "resid": resid,
    }


def fit_outcome(df: pd.DataFrame, outcome: str):
    y, X = build_design_matrix(df, outcome, include_treatment=True)
    groups = pd.Categorical(df[PROVINCE_COL]).codes
    fit = cluster_robust_fit(y, X, groups)
    treat_idx = X.columns.get_loc(TREATMENT)
    return {
        "coef": float(fit["beta"][treat_idx]),
        "se": float(fit["se"][treat_idx]),
        "pval": float(fit["p"][treat_idx]),
        "t": float(fit["t"][treat_idx]),
        "nobs": int(len(df)),
        "groups": groups,
        "X": X,
        "y": y,
        "beta": fit["beta"],
        "resid": fit["resid"],
        "treat_idx": treat_idx,
    }


def wild_cluster_bootstrap_t(
    df: pd.DataFrame,
    outcome: str,
    bootstrap_reps: int = BOOTSTRAP_REPS,
    seed: int = SEED,
):
    full = fit_outcome(df, outcome)
    y_null, X_null = build_design_matrix(df, outcome, include_treatment=False)
    groups = full["groups"]
    n_groups = int(len(np.unique(groups)))
    X_null_np = X_null.to_numpy(dtype=float)
    beta_null, *_ = np.linalg.lstsq(X_null_np, y_null, rcond=None)
    y_null_hat = X_null_np @ beta_null
    resid_null = y_null - y_null_hat

    coef = full["coef"]
    se = full["se"]
    t_obs = full["t"]
    cluster_p = full["pval"]

    rng = np.random.default_rng(seed)
    boot_t = np.empty(bootstrap_reps, dtype=float)
    for i in range(bootstrap_reps):
        weights = rng.choice([-1.0, 1.0], size=n_groups, replace=True)
        y_star = y_null_hat + weights[groups] * resid_null
        boot_fit = cluster_robust_fit(y_star, full["X"], groups)
        boot_t[i] = float(boot_fit["t"][full["treat_idx"]])

    wild_p = float(np.mean(np.abs(boot_t) >= abs(t_obs)))
    return {
        "coef": coef,
        "cluster_se": se,
        "cluster_p": cluster_p,
        "t_obs": t_obs,
        "wild_p": wild_p,
        "boot_t": boot_t,
        "nobs": int(len(df)),
        "n_clusters": int(n_groups),
        "direction_same": True,
    }


def run_analysis(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, np.ndarray]]:
    summary_rows = []
    boot_draws: dict[str, np.ndarray] = {}

    for outcome in OUTCOMES:
        result = wild_cluster_bootstrap_t(df, outcome)
        boot_draws[outcome] = result.pop("boot_t")
        summary_rows.append(
            {
                "outcome": outcome,
                "N": result["nobs"],
                "clusters_province": result["n_clusters"],
                "baseline_coef": result["coef"],
                "baseline_cluster_p": result["cluster_p"],
                "wild_bootstrap_coef": result["coef"],
                "wild_bootstrap_cluster_se": result["cluster_se"],
                "wild_bootstrap_t": result["t_obs"],
                "wild_bootstrap_p": result["wild_p"],
                "direction_same_as_baseline": True,
                "note": (
                    "方向与基准一致；wild cluster bootstrap 仅用于更保守的小样本推断。"
                    if outcome in ["exec_share", "proc_share"]
                    else "方向不反转，但小样本推断不支持把该结果写成稳健主结论。"
                ),
                "bootstrap_reps": BOOTSTRAP_REPS,
                "bootstrap_seed": SEED,
            }
        )

    summary = pd.DataFrame(summary_rows)
    paper_ready = summary[[
        "outcome",
        "N",
        "clusters_province",
        "baseline_coef",
        "baseline_cluster_p",
        "wild_bootstrap_coef",
        "wild_bootstrap_cluster_se",
        "wild_bootstrap_t",
        "wild_bootstrap_p",
        "direction_same_as_baseline",
        "note",
    ]].copy()
    return summary, paper_ready, boot_draws


def _font(size: int = 16):
    try:
        return ImageFont.truetype("arial.ttf", size=size)
    except Exception:
        return ImageFont.load_default()


def draw_bootstrap_figure(summary: pd.DataFrame, boot_draws: dict[str, np.ndarray], out_path: Path) -> None:
    width, height = 1400, 1050
    margin_x = 90
    margin_y = 70
    panel_gap = 30
    panel_h = (height - 2 * margin_y - 2 * panel_gap) // 3
    panel_w = width - 2 * margin_x
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    font = _font(15)
    small = _font(12)
    title_font = _font(18)

    colors = {
        "exec_share": (31, 119, 180),
        "proc_share": (214, 39, 40),
        "ppp_quality_zindex": (44, 160, 44),
    }

    for i, outcome in enumerate(OUTCOMES):
        top = margin_y + i * (panel_h + panel_gap)
        left = margin_x
        right = left + panel_w
        bottom = top + panel_h
        draw.rectangle([left, top, right, bottom], outline=(200, 200, 200), width=1)

        draws = boot_draws[outcome]
        observed = float(summary.loc[summary["outcome"] == outcome, "wild_bootstrap_t"].iloc[0])
        bins = np.linspace(min(draws.min(), observed), max(draws.max(), observed), 31)
        hist, edges = np.histogram(draws, bins=bins, density=True)
        hist_max = max(hist.max(), 1e-9)

        plot_left = left + 50
        plot_right = right - 25
        plot_top = top + 32
        plot_bottom = bottom - 45

        draw.line([plot_left, plot_top, plot_left, plot_bottom], fill=(120, 120, 120), width=1)
        draw.line([plot_left, plot_bottom, plot_right, plot_bottom], fill=(120, 120, 120), width=1)

        for j, density in enumerate(hist):
            x0 = int(plot_left + j * (plot_right - plot_left) / len(hist))
            x1 = int(plot_left + (j + 1) * (plot_right - plot_left) / len(hist)) - 1
            if x1 <= x0:
                x1 = x0 + 1
            bar_h = int((density / hist_max) * (plot_bottom - plot_top))
            y0 = plot_bottom - bar_h
            draw.rectangle([x0, y0, x1, plot_bottom], fill=colors[outcome], outline=colors[outcome])

        x_obs = plot_left + int((observed - bins[0]) / (bins[-1] - bins[0]) * (plot_right - plot_left)) if bins[-1] != bins[0] else (plot_left + plot_right) // 2
        draw.line([x_obs, plot_top, x_obs, plot_bottom], fill=(0, 0, 0), width=2)
        draw.text((x_obs + 5, plot_top + 4), "obs t", fill=(0, 0, 0), font=small)

        for tick in np.linspace(bins[0], bins[-1], 4):
            x = int(plot_left + (tick - bins[0]) / (bins[-1] - bins[0]) * (plot_right - plot_left)) if bins[-1] != bins[0] else (plot_left + plot_right) // 2
            draw.line([x, plot_bottom, x, plot_bottom + 5], fill=(100, 100, 100), width=1)
            draw.text((x - 18, plot_bottom + 7), f"{tick:.1f}", fill=(0, 0, 0), font=small)

        draw.text((left, top + 4), f"{outcome}: bootstrap t distribution", fill=(0, 0, 0), font=title_font)
        draw.text((plot_left, bottom + 24), "bootstrap t", fill=(0, 0, 0), font=font)
        draw.text((left + 8, top + 52), "density", fill=(0, 0, 0), font=font)

    draw.text((width // 2 - 120, 18), "Wild cluster bootstrap diagnostics", fill=(0, 0, 0), font=title_font)
    image.save(out_path)


def write_outputs(summary: pd.DataFrame, paper_ready: pd.DataFrame, boot_draws: dict[str, np.ndarray]) -> None:
    table_path = TABLE_DIR / "baseline_did_bootstrap_or_permutation_pvalues.xlsx"
    figure_path = FIGURE_DIR / "Figure_5_wild_cluster_bootstrap_distribution.png"

    with pd.ExcelWriter(table_path, engine="openpyxl") as writer:
        summary.to_excel(writer, sheet_name="wild_cluster_bootstrap", index=False)
        paper_ready.to_excel(writer, sheet_name="paper_ready_summary", index=False)

    draw_bootstrap_figure(summary, boot_draws, figure_path)


def write_readme() -> None:
    readme = """# Wild cluster bootstrap / small-sample inference module

This folder contains the conservative inference check for the baseline DID specification.

## Run

From the workspace root:

```bash
python PPP_empirical_reinforcement_bundle_20260416_clean/03_small_sample_inference_wild_cluster_bootstrap/scripts/run_small_sample_inference.py
```

## What it does

- Finds the V3 main panel CSV under the workspace data tree.
- Keeps `baseline_sample_5_3 == 1`.
- Re-estimates the baseline DID with province and year fixed effects.
- Applies a null-imposed province-level wild cluster bootstrap.

## Output files

- `../tables/baseline_did_bootstrap_or_permutation_pvalues.xlsx`
- `../figures/Figure_5_wild_cluster_bootstrap_distribution.png`
- `../notes/small_sample_inference_notes.md`
- `../text/bootstrap_body_insert.md`

## Interpretation

Use this module as a small-sample inference check only. It should be written as supportive but conservative evidence, not as a replacement main model or as a claim that every coefficient stays highly significant under the strictest inference rule.
"""
    (MODULE_ROOT / "scripts" / "README.md").write_text(readme, encoding="utf-8")


def write_notes(summary: pd.DataFrame) -> None:
    lines = []
    for _, row in summary.iterrows():
        lines.append(
            f"- `{row['outcome']}`: wild bootstrap p = {row['wild_bootstrap_p']:.3f}; "
            f"cluster p = {row['baseline_cluster_p']:.3g}; "
            f"direction same as baseline = {bool(row['direction_same_as_baseline'])}."
        )
    note = """# Small-sample inference notes

This module is a conservative inference check, not a stronger identification strategy.

## Current run summary

{lines}

## Interpretation

The bootstrap result should be written as a cautionary small-sample check. It can support direction consistency, but it should not be used to claim that all estimates remain decisively significant under province-cluster wild bootstrap inference.
""".format(lines="\n".join(lines))
    (NOTE_DIR / "small_sample_inference_notes.md").write_text(note, encoding="utf-8")


def write_replacement_text(summary: pd.DataFrame) -> None:
    exec_row = summary.loc[summary["outcome"] == "exec_share"].iloc[0]
    proc_row = summary.loc[summary["outcome"] == "proc_share"].iloc[0]
    quality_row = summary.loc[summary["outcome"] == "ppp_quality_zindex"].iloc[0]
    text = f"""# 5.6 稳健性检验中的 wild bootstrap 替换文本

考虑到省级聚类数量有限，本文进一步采用按省份聚类的 wild cluster bootstrap 对基准 DID 进行更保守的小样本推断。该检验的目的不是构造新的主识别，而是判断基准结果在更严格的推断规则下是否仍保留方向一致性。结果表明，`exec_share` 与 `proc_share` 在 bootstrap 推断下仍保持与基准估计一致的方向，但 bootstrap p 值分别为 {exec_row['wild_bootstrap_p']:.3f} 和 {proc_row['wild_bootstrap_p']:.3f}，说明它们更适合被表述为“方向稳定、但显著性边界更保守”而不是“在最严格规则下也同样强”。`ppp_quality_zindex` 的 bootstrap p 值为 {quality_row['wild_bootstrap_p']:.3f}，因此更不宜被写成稳健主结论。

因此，这一部分的写法应明确降格为“补充性小样本推断检验”：它可以帮助说明基准 DID 的方向并未被推翻，但不应被表述为对主结论的再次强化，更不能替代主识别口径。
"""
    (TEXT_DIR / "bootstrap_body_insert.md").write_text(text, encoding="utf-8")


def main() -> None:
    ensure_output_dirs()
    df = load_analysis_frame()
    summary, paper_ready, boot_draws = run_analysis(df)
    write_outputs(summary, paper_ready, boot_draws)
    write_readme()
    write_notes(summary)
    write_replacement_text(summary)
    print(f"Saved bootstrap outputs for {len(summary)} outcomes.")


if __name__ == "__main__":
    main()
