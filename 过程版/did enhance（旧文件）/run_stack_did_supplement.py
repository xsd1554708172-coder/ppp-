from __future__ import annotations

from pathlib import Path
from typing import Dict, List

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm


ROOT = Path(r"C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目")
PANEL_PATH = ROOT / r"ppp论文数据\01_第3到第8部分_最终修正版\第5部分_核心实证识别\（5.1）识别框架、并表与模型设定\PPP_3.6_model_ready_panel_v3_统一口径_方案2_实际执行版_20260413_1048.csv"
BASELINE_PATH = ROOT / r"ppp论文数据\01_第3到第8部分_最终修正版\第5部分_核心实证识别\（5.3）基准多期DID_TWFE正式回归\PPP_第5部分_5.3正式回归结果长表_V3_重估版_20260413_1048.csv"

OUTPUT_MAIN = ROOT / "PPP_第5部分_stackDID_补充识别结果表.xlsx"
OUTPUT_DYNAMIC = ROOT / "PPP_第5部分_stackDID_动态效应摘要表.xlsx"
OUTPUT_INTENSITY = ROOT / "PPP_第5部分_stackDID_post_onset_intensity_check.xlsx"
OUTPUT_FOREST = ROOT / "Figure_5_stackdid_vs_baseline_forest.png"
OUTPUT_DYNAMIC_FIG = ROOT / "Figure_5_stackdid_dynamic_compact.png"
OUTPUT_TEXT = ROOT / "PPP_第5部分_stackDID_正文替换文本.md"

OUTCOMES = ["exec_share", "proc_share", "ppp_quality_zindex"]
CONTROLS = [
    "dfi",
    "digital_econ",
    "base_station_density",
    "software_gdp_share",
    "it_service_gdp_share",
    "ln_rd_expenditure",
    "ln_tech_contract_value",
    "ln_patent_grants",
    "ln_ppp_doc_n",
    "ln_ppp_inv",
]
BASELINE_SIGN_TARGET = {
    "exec_share": 1,
    "proc_share": -1,
    "ppp_quality_zindex": 1,
}


def setup_fonts() -> None:
    candidates = ["Microsoft YaHei", "SimHei", "SimSun", "Microsoft JhengHei"]
    available = {font.name for font in fm.fontManager.ttflist}
    chosen = next((name for name in candidates if name in available), "DejaVu Sans")
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["font.sans-serif"] = [chosen]
    plt.rcParams["axes.unicode_minus"] = False


def stars(p: float) -> str:
    if pd.isna(p):
        return ""
    if p < 0.01:
        return "***"
    if p < 0.05:
        return "**"
    if p < 0.1:
        return "*"
    return ""


def outcome_cn(name: str) -> str:
    mapping = {
        "exec_share": "执行阶段占比",
        "proc_share": "采购阶段占比",
        "ppp_quality_zindex": "综合治理质量指数",
    }
    return mapping.get(name, name)


def ensure_numeric(df: pd.DataFrame, cols: List[str]) -> pd.DataFrame:
    for col in cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def load_panel() -> pd.DataFrame:
    df = pd.read_csv(PANEL_PATH, encoding="utf-8-sig")
    numeric_cols = OUTCOMES + CONTROLS + [
        "did_any",
        "did_intensity",
        "treat_share",
        "baseline_sample_5_3",
        "year",
    ]
    df = ensure_numeric(df, numeric_cols)
    df = df.loc[df["baseline_sample_5_3"] == 1].copy()
    df["year"] = df["year"].astype(int)
    df["province"] = df["province"].astype(str)
    return df


def first_treat_by_province(df: pd.DataFrame) -> pd.Series:
    treated = (
        df.loc[df["did_any"] > 0, ["province", "year"]]
        .sort_values(["province", "year"])
        .groupby("province")["year"]
        .first()
    )
    return treated


def build_stacked_sample(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    first_treat = first_treat_by_province(df)
    province_meta = pd.DataFrame({"province": sorted(df["province"].unique())})
    province_meta["first_treat"] = province_meta["province"].map(first_treat)
    never = province_meta.loc[province_meta["first_treat"].isna(), "province"].tolist()
    cohorts = sorted(int(x) for x in province_meta["first_treat"].dropna().unique())
    stacks = []
    for cohort in cohorts:
        treated_provinces = province_meta.loc[
            province_meta["first_treat"] == cohort, "province"
        ].tolist()
        subset = df.loc[df["province"].isin(treated_provinces + never)].copy()
        subset["stack_id"] = f"cohort_{cohort}"
        subset["cohort"] = cohort
        subset["treated_cohort"] = subset["province"].isin(treated_provinces).astype(int)
        subset["post"] = (subset["year"] >= cohort).astype(int)
        subset["stack_post"] = subset["treated_cohort"] * subset["post"]
        subset["stack_province"] = subset["stack_id"] + "__" + subset["province"]
        subset["stack_year"] = subset["stack_id"] + "__" + subset["year"].astype(str)
        subset["rel_time"] = np.where(
            subset["treated_cohort"] == 1, subset["year"] - cohort, np.nan
        )
        subset["dyn_lead_le2"] = (
            (subset["treated_cohort"] == 1) & (subset["rel_time"] <= -2)
        ).astype(int)
        subset["dyn_event_0"] = (
            (subset["treated_cohort"] == 1) & (subset["rel_time"] == 0)
        ).astype(int)
        subset["dyn_event_1"] = (
            (subset["treated_cohort"] == 1) & (subset["rel_time"] == 1)
        ).astype(int)
        subset["dyn_event_ge2"] = (
            (subset["treated_cohort"] == 1) & (subset["rel_time"] >= 2)
        ).astype(int)
        subset["post_onset_treat_share"] = subset["stack_post"] * subset["treat_share"]
        subset["post_onset_did_intensity"] = subset["stack_post"] * subset["did_intensity"]
        stacks.append(subset)
    stacked = pd.concat(stacks, ignore_index=True)
    return stacked, province_meta


def fit_clustered(formula: str, data: pd.DataFrame):
    return smf.ols(formula, data=data).fit(
        cov_type="cluster", cov_kwds={"groups": data["province"]}
    )


def load_baseline_results() -> pd.DataFrame:
    df = pd.read_csv(BASELINE_PATH, encoding="utf-8-sig")
    return df.loc[df["did_var"] == "treat_share", ["depvar", "coef", "se", "p", "N"]].copy()


def baseline_map(df: pd.DataFrame) -> Dict[str, Dict[str, float]]:
    return {
        row["depvar"]: {
            "coef": float(row["coef"]),
            "se": float(row["se"]),
            "p": float(row["p"]),
            "N": int(row["N"]),
        }
        for _, row in df.iterrows()
    }


def run_main_models(stacked: pd.DataFrame, base_map: Dict[str, Dict[str, float]]) -> pd.DataFrame:
    rows = []
    control_formula = " + ".join(CONTROLS)
    for outcome in OUTCOMES:
        use = stacked.dropna(subset=[outcome] + CONTROLS).copy()
        formula = f"{outcome} ~ stack_post + {control_formula} + C(stack_province) + C(stack_year)"
        model = fit_clustered(formula, use)
        coef = float(model.params["stack_post"])
        se = float(model.bse["stack_post"])
        pval = float(model.pvalues["stack_post"])
        baseline_coef = base_map[outcome]["coef"]
        same_direction = np.sign(coef) == np.sign(baseline_coef) and coef != 0 and baseline_coef != 0
        rows.append(
            {
                "结果变量": outcome,
                "结果变量中文": outcome_cn(outcome),
                "stack DID系数": coef,
                "聚类标准误": se,
                "p值": pval,
                "显著性": stars(pval),
                "N": int(model.nobs),
                "固定效应说明": "stack_province FE + stack_year FE",
                "聚类层级": "province",
                "控制变量说明": "与V3基准DID一致的10项控制变量",
                "与基准DID方向是否一致": "是" if same_direction else "否",
                "方向边界说明": "方向与基准一致" if same_direction else "方向与基准不一致或接近零",
            }
        )
    return pd.DataFrame(rows)


def run_dynamic_models(stacked: pd.DataFrame) -> pd.DataFrame:
    rows = []
    control_formula = " + ".join(CONTROLS)
    label_map = {
        "dyn_lead_le2": "处理前窗口(<=-2)",
        "dyn_event_0": "当期(0)",
        "dyn_event_1": "后1期",
        "dyn_event_ge2": "后2期及以上",
    }
    for outcome in OUTCOMES:
        use = stacked.dropna(subset=[outcome] + CONTROLS).copy()
        formula = (
            f"{outcome} ~ dyn_lead_le2 + dyn_event_0 + dyn_event_1 + dyn_event_ge2 + "
            f"{control_formula} + C(stack_province) + C(stack_year)"
        )
        model = fit_clustered(formula, use)
        for term, label in label_map.items():
            coef = float(model.params[term])
            pval = float(model.pvalues[term])
            rows.append(
                {
                    "结果变量": outcome,
                    "结果变量中文": outcome_cn(outcome),
                    "窗口": label,
                    "系数": coef,
                    "聚类标准误": float(model.bse[term]),
                    "p值": pval,
                    "显著性": stars(pval),
                    "方向": "正向" if coef > 0 else ("负向" if coef < 0 else "零"),
                    "边界说明": (
                        "若处理前窗口显著，需提示识别边界；不得解释为平行趋势成立。"
                        if label == "处理前窗口(<=-2)"
                        else "用于刻画动态方向，不改变主识别结构。"
                    ),
                    "N": int(model.nobs),
                }
            )
    return pd.DataFrame(rows)


def run_post_onset_intensity(stacked: pd.DataFrame) -> pd.DataFrame:
    rows = []
    control_formula = " + ".join(CONTROLS)
    for reg in ["post_onset_treat_share", "post_onset_did_intensity"]:
        for outcome in OUTCOMES:
            use = stacked.dropna(subset=[outcome] + CONTROLS).copy()
            formula = f"{outcome} ~ {reg} + {control_formula} + C(stack_province) + C(stack_year)"
            model = fit_clustered(formula, use)
            coef = float(model.params[reg])
            rows.append(
                {
                    "结果变量": outcome,
                    "结果变量中文": outcome_cn(outcome),
                    "附加强度变量": reg,
                    "系数": coef,
                    "聚类标准误": float(model.bse[reg]),
                    "p值": float(model.pvalues[reg]),
                    "显著性": stars(float(model.pvalues[reg])),
                    "方向是否与主结果一致": "是" if np.sign(coef) == BASELINE_SIGN_TARGET[outcome] and coef != 0 else "否",
                    "N": int(model.nobs),
                    "备注": "仅作进入处理后的强度附检，不进入正文主结论。",
                }
            )
    return pd.DataFrame(rows)


def write_excels(main_df: pd.DataFrame, dynamic_df: pd.DataFrame, intensity_df: pd.DataFrame, province_meta: pd.DataFrame) -> None:
    with pd.ExcelWriter(OUTPUT_MAIN, engine="openpyxl") as writer:
        main_df.to_excel(writer, index=False, sheet_name="stack_did_main")
        province_meta.to_excel(writer, index=False, sheet_name="cohort_map")
    with pd.ExcelWriter(OUTPUT_DYNAMIC, engine="openpyxl") as writer:
        dynamic_df.to_excel(writer, index=False, sheet_name="dynamic_long")
        dynamic_df.pivot_table(
            index="结果变量中文", columns="窗口", values="系数", aggfunc="first"
        ).reset_index().to_excel(writer, index=False, sheet_name="dynamic_summary")
    with pd.ExcelWriter(OUTPUT_INTENSITY, engine="openpyxl") as writer:
        intensity_df.to_excel(writer, index=False, sheet_name="post_onset_intensity")


def draw_forest(main_df: pd.DataFrame, baseline_df: pd.DataFrame) -> None:
    merged = main_df.merge(
        baseline_df.rename(
            columns={
                "depvar": "结果变量",
                "coef": "baseline_coef",
                "se": "baseline_se",
                "p": "baseline_p",
            }
        ),
        on="结果变量",
        how="left",
    )
    merged["baseline_low"] = merged["baseline_coef"] - 1.96 * merged["baseline_se"]
    merged["baseline_high"] = merged["baseline_coef"] + 1.96 * merged["baseline_se"]
    merged["stack_low"] = merged["stack DID系数"] - 1.96 * merged["聚类标准误"]
    merged["stack_high"] = merged["stack DID系数"] + 1.96 * merged["聚类标准误"]
    order = list(reversed(range(len(merged))))
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.8), sharey=True)
    specs = [
        ("baseline_coef", "baseline_low", "baseline_high", "基准DID (treat_share)", "#1f4e79"),
        ("stack DID系数", "stack_low", "stack_high", "补充识别：stack DID", "#7f1d1d"),
    ]
    for ax, spec in zip(axes, specs):
        coef_col, low_col, high_col, title, color = spec
        ax.axvline(0, color="grey", linestyle="--", linewidth=1)
        for y, (_, row) in zip(order, merged.iterrows()):
            ax.plot([row[low_col], row[high_col]], [y, y], color=color, linewidth=2)
            ax.scatter(row[coef_col], y, color=color, s=35, zorder=3)
        ax.set_title(title, fontsize=11)
        ax.set_yticks(order)
        ax.set_yticklabels(merged["结果变量中文"].tolist(), fontsize=10)
        ax.grid(axis="x", alpha=0.2)
    fig.suptitle("基准DID与stack DID结果对比", fontsize=12)
    plt.tight_layout()
    plt.savefig(OUTPUT_FOREST, dpi=300, bbox_inches="tight")
    plt.close(fig)


def draw_dynamic(dynamic_df: pd.DataFrame) -> None:
    order = ["处理前窗口(<=-2)", "当期(0)", "后1期", "后2期及以上"]
    fig, axes = plt.subplots(1, 3, figsize=(11.5, 3.8))
    for ax, outcome in zip(axes, OUTCOMES):
        sub = dynamic_df.loc[dynamic_df["结果变量"] == outcome].copy()
        sub["窗口"] = pd.Categorical(sub["窗口"], categories=order, ordered=True)
        sub = sub.sort_values("窗口")
        xs = np.arange(len(sub))
        lows = sub["系数"] - 1.96 * sub["聚类标准误"]
        highs = sub["系数"] + 1.96 * sub["聚类标准误"]
        ax.axhline(0, color="grey", linestyle="--", linewidth=1)
        ax.vlines(xs, lows, highs, color="#1f4e79", linewidth=2)
        ax.scatter(xs, sub["系数"], color="#1f4e79", s=28, zorder=3)
        ax.set_xticks(xs)
        ax.set_xticklabels(order, rotation=20, ha="right", fontsize=8)
        ax.set_title(outcome_cn(outcome), fontsize=10)
        ax.grid(axis="y", alpha=0.2)
    fig.suptitle("stack DID动态效应压缩展示", fontsize=12)
    plt.tight_layout()
    plt.savefig(OUTPUT_DYNAMIC_FIG, dpi=300, bbox_inches="tight")
    plt.close(fig)


def write_replacement_text(main_df: pd.DataFrame) -> None:
    exec_row = main_df.loc[main_df["结果变量"] == "exec_share"].iloc[0]
    proc_row = main_df.loc[main_df["结果变量"] == "proc_share"].iloc[0]
    qual_row = main_df.loc[main_df["结果变量"] == "ppp_quality_zindex"].iloc[0]

    main_sentence = (
        "执行阶段占比和采购阶段占比的核心方向判断在更稳健的处理进入框架下保持一致，说明推进结构改善这一主结论并不依赖于经典TWFE设定。"
        if exec_row["与基准DID方向是否一致"] == "是" and proc_row["与基准DID方向是否一致"] == "是"
        else "补充识别框架下估计强度存在一定波动，说明主结论在方向上较稳，但统计强度仍受识别设定影响，应继续保持边界意识。"
    )
    fluctuation_sentence = "补充识别框架下估计强度存在一定波动，说明主结论在方向上较稳，但统计强度仍受识别设定影响，应继续保持边界意识。"
    if qual_row["stack DID系数"] > 0 and qual_row["p值"] >= 0.1:
        quality_sentence = "质量型口径在补充识别框架下仍未形成足够稳定的统计支持，因此其更适合被理解为边际改善信号，而非全文主结论。"
    elif qual_row["与基准DID方向是否一致"] != "是":
        quality_sentence = "质量型口径在补充识别框架下未形成与推进结构结果同等稳定的方向支持，因此不宜被抬升为全文主结论。"
    else:
        quality_sentence = "质量型口径在补充识别框架下未显示出与推进结构结果同等稳定的支持，因此仍应保持降调表述。"
    boundary_sentence = (
        fluctuation_sentence
        if any(main_df["p值"] >= 0.1)
        else "整体上看，补充识别结果强化了方向判断，但本文仍将其定位为对主识别的补充检验，而非替代框架。"
    )
    text = f"""# 第4章 4.4 新增一句方法预告

鉴于多期处理情形下经典TWFE估计可能受到处理时点异质性影响，后文进一步采用基于首次进入处理时点的stack DID作为补充识别检验，以考察核心推进结构结论在更稳健处理框架下是否保持一致。

# 第5章 5.3 结尾新增一句过渡

基于上述识别边界，本文在后续稳健性部分进一步采用以处理进入时点为基础的stack DID进行补充检验，以降低经典多期DID结果对处理时点结构的依赖。

# 第5章 5.6 新增小节“补充识别检验：Stack DID”

为进一步降低经典多期DID/TWFE在处理时点异质性下可能带来的估计偏差，本文在不改变`treat_share`作为全文主识别变量的前提下，额外采用基于首次进入处理状态的stack DID进行补充检验。具体而言，本文以`did_any`首次由0转为1的年份界定处理进入时点，并以never-treated省份作为对照组，在当前正式有效样本口径内构造cohort对齐的stacked样本。表X报告了三项核心结果变量的补充识别结果，图X进一步将其与基准DID估计并列展示。{main_sentence}{quality_sentence}{boundary_sentence}因此，stack DID更适合作为对主结果方向稳定性的补充核查，而不改变本文以`treat_share`多期DID/TWFE为唯一主识别的论文结构。
"""
    OUTPUT_TEXT.write_text(text, encoding="utf-8")


def verify_outputs(paths: List[Path]) -> None:
    missing = [str(p) for p in paths if not p.exists()]
    if missing:
        raise FileNotFoundError("Missing outputs: " + ", ".join(missing))


def main() -> None:
    setup_fonts()
    baseline_df = load_baseline_results()
    base_map = baseline_map(baseline_df)
    panel = load_panel()
    stacked, province_meta = build_stacked_sample(panel)
    main_df = run_main_models(stacked, base_map)
    dynamic_df = run_dynamic_models(stacked)
    intensity_df = run_post_onset_intensity(stacked)
    write_excels(main_df, dynamic_df, intensity_df, province_meta)
    draw_forest(main_df, baseline_df)
    draw_dynamic(dynamic_df)
    write_replacement_text(main_df)
    verify_outputs(
        [
            OUTPUT_MAIN,
            OUTPUT_DYNAMIC,
            OUTPUT_INTENSITY,
            OUTPUT_FOREST,
            OUTPUT_DYNAMIC_FIG,
            OUTPUT_TEXT,
        ]
    )
    print("Generated outputs:")
    for path in [
        OUTPUT_MAIN,
        OUTPUT_DYNAMIC,
        OUTPUT_INTENSITY,
        OUTPUT_FOREST,
        OUTPUT_DYNAMIC_FIG,
        OUTPUT_TEXT,
    ]:
        print(path)


if __name__ == "__main__":
    main()
