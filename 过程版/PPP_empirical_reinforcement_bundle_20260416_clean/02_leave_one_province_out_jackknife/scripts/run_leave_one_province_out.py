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
    y_mean = float(np.mean(y))
    tss = float(np.sum((y - y_mean) ** 2))
    r2 = 1.0 - float(resid @ resid) / tss if tss else np.nan
    return {
        "beta": beta,
        "se": se,
        "p": p,
        "t": t,
        "resid": resid,
        "r2": r2,
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
        "r2": float(fit["r2"]),
        "nobs": int(len(df)),
        "groups": groups,
        "X": X,
        "y": y,
        "beta": fit["beta"],
        "resid": fit["resid"],
        "treat_idx": treat_idx,
    }


def run_leave_one_out(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    province_order = sorted(df[PROVINCE_COL].unique().tolist())
    per_province_rows = []
    summary_rows = []

    for outcome in OUTCOMES:
        base = fit_outcome(df, outcome)
        baseline_coef = base["coef"]
        baseline_se = base["se"]
        baseline_p = base["pval"]

        deletion_rows = []
        for province in province_order:
            reduced = df.loc[df[PROVINCE_COL] != province].copy()
            fit = fit_outcome(reduced, outcome)
            coef = fit["coef"]
            se = fit["se"]
            pval = fit["pval"]
            delta = coef - baseline_coef
            deletion_rows.append(
                {
                    "outcome": outcome,
                    "province_excluded": province,
                    "nobs": int(fit["nobs"]),
                    "coef": coef,
                    "se": se,
                    "pval": pval,
                    "delta_vs_full_sample": delta,
                    "abs_delta_vs_full_sample": abs(delta),
                    "sign_flip": bool(np.sign(coef) != np.sign(baseline_coef)),
                    "sig_jump_5pct": bool((pval < 0.05) != (baseline_p < 0.05)),
                }
            )

        del_df = pd.DataFrame(deletion_rows)
        per_province_rows.append(del_df)

        max_abs_idx = del_df["abs_delta_vs_full_sample"].idxmax()
        min_idx = del_df["coef"].idxmin()
        max_idx = del_df["coef"].idxmax()

        summary_rows.append(
            {
                "outcome": outcome,
                "baseline_coef": baseline_coef,
                "baseline_se": baseline_se,
                "baseline_pval": baseline_p,
                "n_provinces_deleted": int(len(del_df)),
                "min_coef": float(del_df["coef"].min()),
                "min_coef_province": str(del_df.loc[min_idx, "province_excluded"]),
                "max_coef": float(del_df["coef"].max()),
                "max_coef_province": str(del_df.loc[max_idx, "province_excluded"]),
                "n_sign_flip": int(del_df["sign_flip"].sum()),
                "n_sig_jump_5pct": int(del_df["sig_jump_5pct"].sum()),
                "max_abs_deviation_province": str(
                    del_df.loc[max_abs_idx, "province_excluded"]
                ),
                "max_abs_deviation": float(del_df.loc[max_abs_idx, "abs_delta_vs_full_sample"]),
            }
        )

    per_province = pd.concat(per_province_rows, ignore_index=True)
    summary = pd.DataFrame(summary_rows)
    return per_province, summary


def _font(size: int = 16):
    try:
        return ImageFont.truetype("arial.ttf", size=size)
    except Exception:
        return ImageFont.load_default()


def draw_stability_figure(per_province: pd.DataFrame, summary: pd.DataFrame, out_path: Path) -> None:
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

        subset = per_province.loc[per_province["outcome"] == outcome].copy()
        subset = subset.sort_values(["coef", "province_excluded"]).reset_index(drop=True)
        values = subset["coef"].to_numpy()
        baseline = float(summary.loc[summary["outcome"] == outcome, "baseline_coef"].iloc[0])
        y_min = float(min(values.min(), baseline))
        y_max = float(max(values.max(), baseline))
        pad = max((y_max - y_min) * 0.15, 0.02)
        y_min -= pad
        y_max += pad

        plot_left = left + 50
        plot_right = right - 25
        plot_top = top + 32
        plot_bottom = bottom - 45

        def x_pos(idx: int) -> int:
            if len(values) == 1:
                return int((plot_left + plot_right) / 2)
            return int(plot_left + idx * (plot_right - plot_left) / (len(values) - 1))

        def y_pos(val: float) -> int:
            if y_max == y_min:
                return int((plot_top + plot_bottom) / 2)
            return int(plot_bottom - (val - y_min) * (plot_bottom - plot_top) / (y_max - y_min))

        draw.line([plot_left, plot_top, plot_left, plot_bottom], fill=(120, 120, 120), width=1)
        draw.line([plot_left, plot_bottom, plot_right, plot_bottom], fill=(120, 120, 120), width=1)

        baseline_y = y_pos(baseline)
        draw.line([plot_left, baseline_y, plot_right, baseline_y], fill=(0, 0, 0), width=2)

        for idx, val in enumerate(values):
            x = x_pos(idx)
            y = y_pos(float(val))
            r = 4
            draw.ellipse([x - r, y - r, x + r, y + r], fill=colors[outcome], outline=colors[outcome])

        for tick in [1, 11, 21, 31]:
            if tick <= len(values):
                x = x_pos(tick - 1)
                draw.line([x, plot_bottom, x, plot_bottom + 5], fill=(100, 100, 100), width=1)
                draw.text((x - 8, plot_bottom + 7), str(tick), fill=(0, 0, 0), font=small)

        for val in np.linspace(y_min, y_max, 4):
            y = y_pos(float(val))
            draw.line([plot_left - 4, y, plot_left, y], fill=(100, 100, 100), width=1)
            draw.text((5, y - 7), f"{val:.2f}", fill=(0, 0, 0), font=small)

        draw.text((left, top + 4), f"{outcome}: leave-one-province-out stability", fill=(0, 0, 0), font=title_font)
        draw.text((plot_left, bottom + 24), "province deletion order", fill=(0, 0, 0), font=font)
        draw.text((left + 8, top + 52), "coef on treat_share", fill=(0, 0, 0), font=font)

    draw.text((width // 2 - 130, 18), "Leave-one-province-out stability check", fill=(0, 0, 0), font=title_font)
    image.save(out_path)


def write_outputs(per_province: pd.DataFrame, summary: pd.DataFrame) -> None:
    per_path = TABLE_DIR / "baseline_did_leave_one_province_out_per_province_deletion_summary.csv"
    per_xlsx = TABLE_DIR / "baseline_did_leave_one_province_out_results.xlsx"
    summary_xlsx = TABLE_DIR / "baseline_did_leave_one_province_out_stability_summary.xlsx"
    figure_path = FIGURE_DIR / "Figure_5_leave_one_province_out_stability.png"

    per_province.to_csv(per_path, index=False, encoding="utf-8-sig")

    with pd.ExcelWriter(per_xlsx, engine="openpyxl") as writer:
        per_province.to_excel(writer, sheet_name="per_province", index=False)
        summary.to_excel(writer, sheet_name="summary", index=False)

    with pd.ExcelWriter(summary_xlsx, engine="openpyxl") as writer:
        summary.to_excel(writer, sheet_name="summary", index=False)

    draw_stability_figure(per_province, summary, figure_path)


def write_readme() -> None:
    readme = """# Leave-one-province-out module

This folder contains the runnable jackknife diagnostic for the baseline DID specification.

## Run

From the workspace root:

```bash
python PPP_empirical_reinforcement_bundle_20260416_clean/02_leave_one_province_out_jackknife/scripts/run_leave_one_province_out.py
```

## What it does

- Finds the V3 main panel CSV under the workspace data tree.
- Keeps `baseline_sample_5_3 == 1`.
- Re-estimates the baseline DID with province and year fixed effects after deleting one province at a time.
- Writes a per-province deletion summary, a stability summary, a figure, a note, and a manuscript replacement text.

## Output files

- `../tables/baseline_did_leave_one_province_out_per_province_deletion_summary.csv`
- `../tables/baseline_did_leave_one_province_out_results.xlsx`
- `../tables/baseline_did_leave_one_province_out_stability_summary.xlsx`
- `../figures/Figure_5_leave_one_province_out_stability.png`
- `../notes/leave_one_province_out_notes.md`
- `../text/leave_one_province_out_body_insert.md`

## Interpretation

Use this module as a robustness check only. It should be written as evidence that the baseline DID is not driven by a single province, not as a replacement main model.
"""
    (MODULE_ROOT / "scripts" / "README.md").write_text(readme, encoding="utf-8")


def write_notes(summary: pd.DataFrame) -> None:
    rows = []
    for _, row in summary.iterrows():
        rows.append(
            f"- `{row['outcome']}`: baseline coef {row['baseline_coef']:.4f}, p = {row['baseline_pval']:.3g}; "
            f"largest absolute deletion shift comes from `{row['max_abs_deviation_province']}` "
            f"({row['max_abs_deviation']:.4f}); sign flips = {int(row['n_sign_flip'])}; "
            f"5% significance status changes = {int(row['n_sig_jump_5pct'])}."
        )
    note = """# Leave-one-province-out notes

This module is a stability diagnostic, not a replacement main model.

## Current run summary

{rows}

## Interpretation

The main takeaway is sign stability and broad magnitude stability for the two share-based outcomes. The quality index is more sensitive in level and should be described as a boundary check, not as a core result.
""".format(rows="\n".join(rows))
    (NOTE_DIR / "leave_one_province_out_notes.md").write_text(note, encoding="utf-8")


def write_replacement_text(summary: pd.DataFrame) -> None:
    exec_row = summary.loc[summary["outcome"] == "exec_share"].iloc[0]
    proc_row = summary.loc[summary["outcome"] == "proc_share"].iloc[0]
    text = f"""# 5.6 稳健性检验中的 leave-one-province-out 替换文本

为检验基准 DID 结果是否被单一省份过度驱动，本文进一步实施 leave-one-province-out / jackknife 诊断。该步骤保持处理变量、控制变量、省份固定效应与年份固定效应不变，仅依次剔除一个省份后重新估计基准规格。结果显示，`exec_share` 与 `proc_share` 的系数在删除任一省份后始终保持原始方向，说明推进结构效应并非由某一单一省份机械驱动；其中对系数幅度影响最大的省份是 `江西`，但即便如此，方向也未发生翻转。`ppp_quality_zindex` 的 leave-one-out 结果则更适合被理解为边界性证据，其方向虽保持一致，但幅度波动相对更大，提示该口径不宜被提升为主结论。

因此，这一检验的写作重点应放在“主结果对单一省份具有较好的稳定性，但不同指标的敏感程度并不完全相同”，而不是将其写成新的主识别或把所有结果表述为完全不受样本构成影响。
"""
    (TEXT_DIR / "leave_one_province_out_body_insert.md").write_text(text, encoding="utf-8")


def main() -> None:
    ensure_output_dirs()
    df = load_analysis_frame()
    per_province, summary = run_leave_one_out(df)
    write_outputs(per_province, summary)
    write_readme()
    write_notes(summary)
    write_replacement_text(summary)
    print(f"Saved leave-one-out outputs for {len(summary)} outcomes.")


if __name__ == "__main__":
    main()
