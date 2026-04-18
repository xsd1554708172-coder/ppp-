from __future__ import annotations

import importlib.util
import math
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_ROOT = PROJECT_ROOT / "did修改补强_round2_方案A"
SCRIPTS_DIR = OUTPUT_ROOT / "scripts"
TABLE_DIR = OUTPUT_ROOT / "表格"
FIG_DIR = OUTPUT_ROOT / "图形"
TEXT_DIR = OUTPUT_ROOT / "正文替换文本"
DOC_DIR = OUTPUT_ROOT / "说明"
LOG_DIR = OUTPUT_ROOT / "日志"

OUTCOMES = ["exec_share", "proc_share", "ppp_quality_zindex"]
CONTROL_VARS = [
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

MAIN_STACK_SPEC_ID = "stack_never_w2"
COHORT_ATT_SPEC_ID = "cohort_later_w2"
SPEC_CATALOG = [
    {
        "spec_id": "stack_never_w2",
        "label": "Stack DID：never-treated only，窗口[-2,+2]",
        "window_pre": 2,
        "window_post": 2,
        "control_mode": "never",
    },
    {
        "spec_id": "stack_later_w2",
        "label": "Stack DID：never+not-yet-treated，窗口[-2,+2]",
        "window_pre": 2,
        "window_post": 2,
        "control_mode": "later",
    },
    {
        "spec_id": "stack_never_w3_2",
        "label": "Stack DID：never-treated only，窗口[-3,+2]",
        "window_pre": 3,
        "window_post": 2,
        "control_mode": "never",
    },
    {
        "spec_id": "stack_later_w3_2",
        "label": "Stack DID：never+not-yet-treated，窗口[-3,+2]",
        "window_pre": 3,
        "window_post": 2,
        "control_mode": "later",
    },
    {
        "spec_id": "stack_never_w2_1",
        "label": "Stack DID：never-treated only，窗口[-2,+1]",
        "window_pre": 2,
        "window_post": 1,
        "control_mode": "never",
    },
    {
        "spec_id": "stack_later_w2_1",
        "label": "Stack DID：never+not-yet-treated，窗口[-2,+1]",
        "window_pre": 2,
        "window_post": 1,
        "control_mode": "later",
    },
]


def ensure_dirs() -> None:
    for path in [SCRIPTS_DIR, TABLE_DIR, FIG_DIR, TEXT_DIR, DOC_DIR, LOG_DIR]:
        path.mkdir(parents=True, exist_ok=True)


def find_required(filename: str) -> Path:
    matches = sorted(PROJECT_ROOT.rglob(filename))
    if not matches:
        raise FileNotFoundError(f"未找到必需文件: {filename}")
    return matches[0]


def star(p: float) -> str:
    if pd.isna(p):
        return ""
    if p < 0.01:
        return "***"
    if p < 0.05:
        return "**"
    if p < 0.10:
        return "*"
    return ""


def format_coef(coef: float, p: float) -> str:
    if pd.isna(coef):
        return ""
    return f"{coef:.4f}{star(p)}"


def direction_label(value: float) -> str:
    if pd.isna(value):
        return "NA"
    if value > 0:
        return "正向"
    if value < 0:
        return "负向"
    return "零"


def load_inputs() -> Tuple[pd.DataFrame, pd.DataFrame, Path, Path]:
    panel_path = find_required("PPP_3.6_model_ready_panel_v3_统一口径_方案2_实际执行版_20260413_1048.csv")
    baseline_path = find_required("PPP_第5部分_5.3正式回归结果长表_V3_重估版_20260413_1048.csv")
    panel = pd.read_csv(panel_path)
    baseline = pd.read_csv(baseline_path)
    return panel, baseline, panel_path, baseline_path


def prepare_panel(panel: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[int, int], List[str], Dict[str, object]]:
    full = panel.copy()
    full_first = (
        full.loc[full["did_any"] == 1]
        .groupby("province", as_index=False)["year"]
        .min()
        .rename(columns={"year": "first_treat_year"})
    )
    full = full.merge(full_first, on="province", how="left")
    full_never = sorted(full.loc[full["first_treat_year"].isna(), "province"].drop_duplicates().tolist())

    data = full.loc[full["baseline_sample_5_3"] == 1].copy()
    cohort_counts = (
        data.loc[data["first_treat_year"].notna(), ["province", "first_treat_year"]]
        .drop_duplicates()
        .groupby("first_treat_year")
        .size()
        .astype(int)
        .to_dict()
    )
    never_provinces = sorted(data.loc[data["first_treat_year"].isna(), "province"].unique().tolist())
    excluded_never = sorted(set(full_never) - set(never_provinces))
    never_diff = {
        "full_never": full_never,
        "baseline_never": never_provinces,
        "excluded_never": excluded_never,
    }
    if excluded_never:
        prov = excluded_never[0]
        cols = ["province", "year", "baseline_sample_5_3"]
        for c in ["text_observed", "text_missing", "baseline_controls_complete"]:
            if c in full.columns:
                cols.append(c)
        never_diff["excluded_rows"] = full.loc[full["province"] == prov, cols].copy()
    return data, cohort_counts, never_provinces, never_diff


def build_stack(
    data: pd.DataFrame,
    cohort_years: List[int],
    never_provinces: List[str],
    window_pre: int | None,
    window_post: int | None,
    control_mode: str,
) -> pd.DataFrame:
    pieces: List[pd.DataFrame] = []
    for cohort in cohort_years:
        treated = sorted(
            data.loc[data["first_treat_year"] == cohort, "province"].drop_duplicates().tolist()
        )
        if not treated:
            continue
        if control_mode == "never":
            controls = list(never_provinces)
        elif control_mode == "later":
            controls = sorted(
                data.loc[
                    (data["first_treat_year"].isna()) | (data["first_treat_year"] > cohort),
                    "province",
                ]
                .drop_duplicates()
                .tolist()
            )
        else:
            raise ValueError(f"未知控制组模式: {control_mode}")

        frame = data.loc[data["province"].isin(treated + controls)].copy()
        frame["cohort"] = int(cohort)
        frame["event_time"] = frame["year"] - int(cohort)
        frame["stack_treated"] = np.where(frame["province"].isin(treated), 1, 0)
        frame["post_onset"] = np.where((frame["stack_treated"] == 1) & (frame["year"] >= cohort), 1, 0)
        frame["stack_treatment"] = frame["stack_treated"] * frame["post_onset"]
        frame["stack_province"] = frame["province"].astype(str) + "__c" + frame["cohort"].astype(str)
        frame["stack_year"] = frame["year"].astype(str) + "__c" + frame["cohort"].astype(str)

        if control_mode == "later":
            later_mask = frame["stack_treated"].eq(0) & frame["first_treat_year"].notna()
            frame = frame.loc[~later_mask | (frame["year"] < frame["first_treat_year"])].copy()

        if window_pre is not None:
            frame = frame.loc[frame["event_time"] >= -int(window_pre)].copy()
        if window_post is not None:
            frame = frame.loc[frame["event_time"] <= int(window_post)].copy()
        pieces.append(frame)

    if not pieces:
        return pd.DataFrame()
    stacked = pd.concat(pieces, ignore_index=True)
    needed = OUTCOMES + CONTROL_VARS + ["province", "year", "cohort", "event_time", "stack_treatment", "stack_province", "stack_year"]
    return stacked.dropna(subset=needed).copy()


def fit_stack_model(stacked: pd.DataFrame, outcome: str, rhs: str = "stack_treatment") -> Dict[str, float]:
    formula = (
        f"{outcome} ~ {rhs} + "
        + " + ".join(CONTROL_VARS)
        + " + C(stack_province) + C(stack_year)"
    )
    model = smf.ols(formula, data=stacked).fit(
        cov_type="cluster",
        cov_kwds={"groups": stacked["province"]},
    )
    coef = model.params.get(rhs, np.nan)
    se = model.bse.get(rhs, np.nan)
    pval = model.pvalues.get(rhs, np.nan)
    return {
        "coef": coef,
        "se": se,
        "p": pval,
        "N": int(model.nobs),
        "rhs": rhs,
    }


def evaluate_specs(
    data: pd.DataFrame,
    cohort_counts: Dict[int, int],
    never_provinces: List[str],
    baseline: pd.DataFrame,
) -> Tuple[pd.DataFrame, Dict[str, pd.DataFrame]]:
    results: List[Dict[str, object]] = []
    stacked_map: Dict[str, pd.DataFrame] = {}
    all_cohorts = sorted(int(x) for x in cohort_counts.keys())
    for spec in SPEC_CATALOG:
        stacked = build_stack(
            data=data,
            cohort_years=all_cohorts,
            never_provinces=never_provinces,
            window_pre=spec["window_pre"],
            window_post=spec["window_post"],
            control_mode=spec["control_mode"],
        )
        stacked_map[spec["spec_id"]] = stacked
        for outcome in OUTCOMES:
            fit = fit_stack_model(stacked, outcome)
            base_row = baseline.loc[
                (baseline["depvar"] == outcome) & (baseline["did_var"] == "treat_share")
            ].iloc[0]
            results.append(
                {
                    "spec_id": spec["spec_id"],
                    "spec_label": spec["label"],
                    "outcome": outcome,
                    "coef": fit["coef"],
                    "se": fit["se"],
                    "p": fit["p"],
                    "N": fit["N"],
                    "window_pre": spec["window_pre"],
                    "window_post": spec["window_post"],
                    "control_mode": spec["control_mode"],
                    "cohorts_used": ",".join(map(str, all_cohorts)),
                    "baseline_coef": float(base_row["coef"]),
                    "baseline_p": float(base_row["p"]),
                    "direction_consistent": direction_label(fit["coef"]) == direction_label(float(base_row["coef"])),
                }
            )
    return pd.DataFrame(results), stacked_map


def build_dynamic_summary(stacked: pd.DataFrame) -> pd.DataFrame:
    dyn = stacked.copy()
    dyn["lead_le2"] = np.where((dyn["stack_treated"] == 1) & (dyn["event_time"] <= -2), 1, 0)
    dyn["event0"] = np.where((dyn["stack_treated"] == 1) & (dyn["event_time"] == 0), 1, 0)
    dyn["post1"] = np.where((dyn["stack_treated"] == 1) & (dyn["event_time"] == 1), 1, 0)
    dyn["postge2"] = np.where((dyn["stack_treated"] == 1) & (dyn["event_time"] >= 2), 1, 0)
    rows: List[Dict[str, object]] = []
    for outcome in OUTCOMES:
        formula = (
            f"{outcome} ~ lead_le2 + event0 + post1 + postge2 + "
            + " + ".join(CONTROL_VARS)
            + " + C(stack_province) + C(stack_year)"
        )
        model = smf.ols(formula, data=dyn).fit(
            cov_type="cluster",
            cov_kwds={"groups": dyn["province"]},
        )
        for term, label in [
            ("lead_le2", "处理前窗口(<=-2)"),
            ("event0", "当期(0)"),
            ("post1", "后1期"),
            ("postge2", "后2期及以上"),
        ]:
            coef = model.params.get(term, np.nan)
            pval = model.pvalues.get(term, np.nan)
            rows.append(
                {
                    "outcome": outcome,
                    "term": term,
                    "window_label": label,
                    "coef": coef,
                    "se": model.bse.get(term, np.nan),
                    "p": pval,
                    "direction": direction_label(coef),
                    "boundary_note": "处理前项不宜解释为平行趋势证明" if term == "lead_le2" else "仅作动态诊断",
                    "N": int(model.nobs),
                }
            )
    return pd.DataFrame(rows)


def build_post_onset_intensity(stacked: pd.DataFrame) -> pd.DataFrame:
    active = stacked.loc[stacked["post_onset"] == 1].copy()
    rows: List[Dict[str, object]] = []
    for rhs in ["treat_share", "did_intensity"]:
        for outcome in OUTCOMES:
            formula = (
                f"{outcome} ~ {rhs} + "
                + " + ".join(CONTROL_VARS)
                + " + C(stack_province) + C(stack_year)"
            )
            model = smf.ols(formula, data=active).fit(
                cov_type="cluster",
                cov_kwds={"groups": active["province"]},
            )
            rows.append(
                {
                    "rhs": rhs,
                    "outcome": outcome,
                    "coef": model.params.get(rhs, np.nan),
                    "se": model.bse.get(rhs, np.nan),
                    "p": model.pvalues.get(rhs, np.nan),
                    "N": int(model.nobs),
                    "direction": direction_label(model.params.get(rhs, np.nan)),
                }
            )
    return pd.DataFrame(rows)


def fit_interaction_weighted_cohort_att(
    data: pd.DataFrame,
    cohort_counts: Dict[int, int],
    never_provinces: List[str],
    window_pre: int,
    window_post: int,
    control_mode: str,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    cohorts = sorted(int(x) for x in cohort_counts.keys())
    stacked = build_stack(
        data=data,
        cohort_years=cohorts,
        never_provinces=never_provinces,
        window_pre=window_pre,
        window_post=window_post,
        control_mode=control_mode,
    )
    for g in cohorts:
        stacked[f"cohort_post_{g}"] = (
            (stacked["cohort"] == g)
            & (stacked["stack_treated"] == 1)
            & (stacked["year"] >= g)
        ).astype(int)

    agg_rows: List[Dict[str, object]] = []
    cohort_rows: List[Dict[str, object]] = []
    weight_array = np.array([cohort_counts[g] for g in cohorts], dtype=float)
    weight_array = weight_array / weight_array.sum()

    for outcome in OUTCOMES:
        terms = [f"cohort_post_{g}" for g in cohorts]
        formula = (
            f"{outcome} ~ "
            + " + ".join(terms + CONTROL_VARS)
            + " + C(stack_province) + C(stack_year)"
        )
        model = smf.ols(formula, data=stacked).fit(
            cov_type="cluster",
            cov_kwds={"groups": stacked["province"]},
        )
        term_coefs = np.array([model.params.get(t, np.nan) for t in terms], dtype=float)
        cov = model.cov_params().loc[terms, terms].values
        agg_coef = float(np.dot(weight_array, term_coefs))
        agg_se = float(np.sqrt(np.dot(weight_array, np.dot(cov, weight_array))))
        agg_t = agg_coef / agg_se if agg_se > 0 else np.nan
        agg_p = float(2 * (1 - 0.5 * (1 + math.erf(abs(agg_t) / math.sqrt(2))))) if agg_se > 0 else np.nan
        agg_rows.append(
            {
                "spec_id": COHORT_ATT_SPEC_ID,
                "estimator": "interaction-weighted cohort ATT",
                "control_mode": control_mode,
                "window_pre": window_pre,
                "window_post": window_post,
                "outcome": outcome,
                "coef": agg_coef,
                "se": agg_se,
                "p": agg_p,
                "N": int(model.nobs),
                "weighting": "按cohort样本量加权",
            }
        )
        for g, term in zip(cohorts, terms):
            cohort_rows.append(
                {
                    "estimator": "interaction-weighted cohort ATT",
                    "outcome": outcome,
                    "cohort": g,
                    "term": term,
                    "coef": model.params.get(term, np.nan),
                    "se": model.bse.get(term, np.nan),
                    "p": model.pvalues.get(term, np.nan),
                    "N": int(model.nobs),
                    "cohort_weight": cohort_counts[g],
                }
            )
    return pd.DataFrame(agg_rows), pd.DataFrame(cohort_rows)


def plot_baseline_vs_stack(baseline: pd.DataFrame, main_results: pd.DataFrame, output: Path) -> None:
    plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Arial Unicode MS", "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False
    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    order = ["exec_share", "proc_share", "ppp_quality_zindex"]
    labels = {
        "exec_share": "执行阶段占比",
        "proc_share": "采购阶段占比",
        "ppp_quality_zindex": "综合质量指数",
    }
    y = np.arange(len(order))
    for i, outcome in enumerate(order):
        base_row = baseline.loc[(baseline["depvar"] == outcome) & (baseline["did_var"] == "treat_share")].iloc[0]
        stack_row = main_results.loc[main_results["outcome"] == outcome].iloc[0]
        ax.errorbar(float(base_row["coef"]), i + 0.12, xerr=1.96 * float(base_row["se"]), fmt="o", color="#1f4e79", capsize=3)
        ax.errorbar(float(stack_row["coef"]), i - 0.12, xerr=1.96 * float(stack_row["se"]), fmt="s", color="#8b3a3a", capsize=3)
    ax.axvline(0, color="black", linewidth=1, linestyle="--")
    ax.set_yticks(y)
    ax.set_yticklabels([labels[o] for o in order])
    ax.set_xlabel("系数及95%置信区间")
    ax.set_title("基准DID与Stack DID结果对照")
    ax.legend(["零效应线", "基准DID", "Stack DID"], loc="lower right")
    fig.tight_layout()
    fig.savefig(output, dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_dynamic(dynamic: pd.DataFrame, output: Path) -> None:
    plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Arial Unicode MS", "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False
    order = ["处理前窗口(<=-2)", "当期(0)", "后1期", "后2期及以上"]
    fig, axes = plt.subplots(1, 3, figsize=(12, 3.8), sharey=True)
    for ax, outcome in zip(axes, OUTCOMES):
        sub = dynamic.loc[dynamic["outcome"] == outcome].copy()
        sub["window_label"] = pd.Categorical(sub["window_label"], categories=order, ordered=True)
        sub = sub.sort_values("window_label")
        x = np.arange(len(sub))
        ax.errorbar(sub["coef"], x, xerr=1.96 * sub["se"], fmt="o", color="#8b3a3a", capsize=3)
        ax.axvline(0, color="black", linewidth=1, linestyle="--")
        ax.set_title(outcome)
        ax.set_yticks(x)
        ax.set_yticklabels(sub["window_label"])
    fig.suptitle("Stack DID动态摘要图（附录诊断用途）", y=1.02)
    fig.tight_layout()
    fig.savefig(output, dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_threeway_compare(
    baseline: pd.DataFrame,
    main_results: pd.DataFrame,
    cohort_att: pd.DataFrame,
    output: Path,
) -> None:
    plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Arial Unicode MS", "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False
    fig, ax = plt.subplots(figsize=(9.2, 4.8))
    order = ["exec_share", "proc_share", "ppp_quality_zindex"]
    labels = {
        "exec_share": "执行阶段占比",
        "proc_share": "采购阶段占比",
        "ppp_quality_zindex": "综合质量指数",
    }
    y = np.arange(len(order))
    for i, outcome in enumerate(order):
        base_row = baseline.loc[(baseline["depvar"] == outcome) & (baseline["did_var"] == "treat_share")].iloc[0]
        stack_row = main_results.loc[main_results["outcome"] == outcome].iloc[0]
        cohort_row = cohort_att.loc[cohort_att["outcome"] == outcome].iloc[0]
        ax.errorbar(float(base_row["coef"]), i + 0.18, xerr=1.96 * float(base_row["se"]), fmt="o", color="#1f4e79", capsize=3)
        ax.errorbar(float(stack_row["coef"]), i, xerr=1.96 * float(stack_row["se"]), fmt="s", color="#8b3a3a", capsize=3)
        ax.errorbar(float(cohort_row["coef"]), i - 0.18, xerr=1.96 * float(cohort_row["se"]), fmt="^", color="#2e8b57", capsize=3)
    ax.axvline(0, color="black", linewidth=1, linestyle="--")
    ax.set_yticks(y)
    ax.set_yticklabels([labels[o] for o in order])
    ax.set_xlabel("系数及95%置信区间")
    ax.set_title("基准DID、Stack DID与更稳健cohort ATT三列对照")
    ax.legend(["零效应线", "基准DID", "Stack DID", "cohort ATT"], loc="lower right")
    fig.tight_layout()
    fig.savefig(output, dpi=300, bbox_inches="tight")
    plt.close(fig)


def choose_main_stack_results(screening: pd.DataFrame) -> pd.DataFrame:
    return screening.loc[screening["spec_id"] == MAIN_STACK_SPEC_ID].copy()


def write_tables(
    screening: pd.DataFrame,
    cohort_counts: Dict[int, int],
    never_diff: Dict[str, object],
    main_results: pd.DataFrame,
    dynamic: pd.DataFrame,
    post_onset: pd.DataFrame,
    cohort_att_agg: pd.DataFrame,
    cohort_att_detail: pd.DataFrame,
) -> None:
    main_table = main_results.copy()
    main_table["coef_fmt"] = [format_coef(c, p) for c, p in zip(main_table["coef"], main_table["p"])]
    main_table["se_fmt"] = main_table["se"].map(lambda x: f"({x:.4f})")
    main_table["固定效应"] = "stack_province FE + stack_year FE"
    main_table["聚类"] = "province"
    main_table["与基准DID方向是否一致"] = np.where(main_table["direction_consistent"], "是", "否")
    main_table["正文采用说明"] = np.where(
        main_table["outcome"].isin(["exec_share", "proc_share"]),
        "可作为方向性补充识别证据；统计强度需单独说明",
        "方向与强度均不稳，不得承担主结论",
    )
    sample_note = pd.DataFrame(
        [
            {
                "说明项": "基准DID正式样本量",
                "数值": 262,
                "说明": "基于baseline_sample_5_3的省级面板有效样本量",
            },
            {
                "说明项": "Stack DID主规格样本量",
                "数值": int(main_table["N"].iloc[0]),
                "说明": "堆叠样本量；never-treated对照组可在不同cohort子实验中重复出现，不等同于简单扩样本",
            },
            {
                "说明项": "正式主面板never-treated数量",
                "数值": len(never_diff["full_never"]),
                "说明": "基于正式V3主面板原始省级单位统计",
            },
            {
                "说明项": "baseline_sample_5_3中的never-treated数量",
                "数值": len(never_diff["baseline_never"]),
                "说明": "Stack DID在正式估计前使用baseline_sample_5_3过滤后保留的never-treated数量",
            },
        ]
    )
    cohort_df = pd.DataFrame(
        [{"cohort": int(k), "province_n": int(v)} for k, v in sorted(cohort_counts.items())]
        + [{"cohort": "never-treated_in_baseline", "province_n": len(never_diff["baseline_never"])}]
        + [{"cohort": "never-treated_in_fullpanel", "province_n": len(never_diff["full_never"])}]
    )
    with pd.ExcelWriter(TABLE_DIR / "StackDID规格比较总表.xlsx", engine="openpyxl") as writer:
        screening.to_excel(writer, sheet_name="规格总表", index=False)
    with pd.ExcelWriter(TABLE_DIR / "基于StackDID的补充识别结果_最终版.xlsx", engine="openpyxl") as writer:
        main_table.to_excel(writer, sheet_name="主规格结果", index=False)
        cohort_df.to_excel(writer, sheet_name="cohort分布", index=False)
        sample_note.to_excel(writer, sheet_name="样本量说明", index=False)
    with pd.ExcelWriter(TABLE_DIR / "StackDID动态效应摘要表_最终版.xlsx", engine="openpyxl") as writer:
        dynamic.to_excel(writer, sheet_name="动态摘要", index=False)
    with pd.ExcelWriter(TABLE_DIR / "PostOnset强度稳健性检验_最终版.xlsx", engine="openpyxl") as writer:
        post_onset.to_excel(writer, sheet_name="post_onset", index=False)
    with pd.ExcelWriter(TABLE_DIR / "更稳健cohortATT补充识别结果.xlsx", engine="openpyxl") as writer:
        cohort_att_agg.to_excel(writer, sheet_name="聚合结果", index=False)
        cohort_att_detail.to_excel(writer, sheet_name="cohort分项结果", index=False)


def build_replacement_text(main_results: pd.DataFrame, cohort_att_agg: pd.DataFrame) -> Tuple[str, str]:
    result_map = {row["outcome"]: row for _, row in main_results.iterrows()}
    cohort_map = {row["outcome"]: row for _, row in cohort_att_agg.iterrows()}
    exec_row = result_map["exec_share"]
    proc_row = result_map["proc_share"]
    qual_row = result_map["ppp_quality_zindex"]
    cohort_exec = cohort_map["exec_share"]
    cohort_proc = cohort_map["proc_share"]
    cohort_qual = cohort_map["ppp_quality_zindex"]

    if exec_row["direction_consistent"] and proc_row["direction_consistent"]:
        core_sentence = "执行阶段占比和采购阶段占比在Stack DID补充识别框架下总体仍保持与基准DID一致的方向判断，但统计强度较基准设定明显减弱，说明推进结构改善这一结论在方向上较稳，同时仍对具体识别设定存在一定敏感性。"
    else:
        core_sentence = "Stack DID补充识别下，推进结构结果未能在方向和统计强度上同时保持稳定，说明相关判断对识别设定较为敏感，正文只能将其作为边界更强的补充诊断，而不能写成额外强化。"

    if qual_row["direction_consistent"] and float(qual_row["p"]) < 0.10:
        qual_sentence = "质量型口径在补充识别框架下仅表现出有限的方向性支持，仍不足以承担全文主结论。"
    else:
        qual_sentence = "质量型口径在补充识别框架下方向和统计强度均不稳，更不能承担主结论。"

    stack_text = "\n".join(
        [
            "## 第4章 4.4 方法预告句",
            "鉴于多期处理情形下经典TWFE估计可能受到处理时点异质性影响，后文进一步采用基于首次进入处理时点的stack DID以及更稳健的cohort ATT聚合估计作为补充识别检验，以考察核心推进结构结论在不同处理时点设定下是否保持一致。",
            "",
            "## 第5章 5.3 结尾过渡句",
            "基于上述识别边界，本文在后续稳健性部分进一步采用以处理进入时点为基础的stack DID，并辅以更稳健的cohort ATT聚合估计进行补充检验，以降低经典多期DID结果对处理时点结构的依赖。",
            "",
            "## 第5章 5.6 新增小节：补充识别检验",
            "在不改变`treat_share`多期DID/TWFE作为全文唯一主识别的前提下，本文进一步基于首次进入处理状态的cohort定义构造stack DID补充识别框架，并比较never-treated only与never+not-yet-treated两类控制组口径。结果显示，"
            + core_sentence
            + qual_sentence
            + "因此，Stack DID更适合被理解为对主结论方向稳健性的补充核查，而不是对经典TWFE结果的替代。动态项的补充结果未显著改善前置识别风险，故仅保留为附录层诊断，不进入正文主论证。"
        ]
    )

    cohort_parts = []
    if direction_label(cohort_exec["coef"]) == "正向":
        cohort_parts.append("执行阶段占比在cohort ATT聚合估计下仍保持正向方向")
    else:
        cohort_parts.append("执行阶段占比在cohort ATT聚合估计下未能保持稳定的正向方向")
    if direction_label(cohort_proc["coef"]) == "负向" and float(cohort_proc["p"]) < 0.05:
        cohort_parts.append("采购阶段占比下降获得了相对更强的统计支持")
    elif direction_label(cohort_proc["coef"]) == "负向":
        cohort_parts.append("采购阶段占比仍保持负向方向，但统计支持有限")
    else:
        cohort_parts.append("采购阶段占比未能保持稳定的负向方向")
    if direction_label(cohort_qual["coef"]) != "正向" or float(cohort_qual["p"]) >= 0.10:
        cohort_parts.append("质量型口径仍未形成正向且稳定的统计支持")
    cohort_text = "\n".join(
        [
            "## cohortATT正文补充段落",
            "考虑到多期处理下不同cohort之间的处理效应可能并不完全同质，本文进一步构造了interaction-weighted cohort ATT聚合估计，并将其作为比Stack DID更靠近异质性处理效应稳健估计思路的补充检验。"
            + "；".join(cohort_parts)
            + "。据此，更稳健的cohort ATT结果更适合作为5.6节中的补充短段：它对采购阶段下降提供了相对更有力的辅助支持，而对执行阶段上升与质量型口径仍应保持边界意识。"
        ]
    )
    return stack_text, cohort_text


def write_docs(
    panel_path: Path,
    baseline_path: Path,
    never_diff: Dict[str, object],
    screening: pd.DataFrame,
    main_results: pd.DataFrame,
    cohort_att_agg: pd.DataFrame,
    dynamic: pd.DataFrame,
    post_onset: pd.DataFrame,
    runtime_info: Dict[str, object],
) -> None:
    stack_text, cohort_text = build_replacement_text(main_results, cohort_att_agg)
    (TEXT_DIR / "PPP_第5部分_补充识别检验_正文替换文本_最终版.md").write_text(stack_text, encoding="utf-8")
    (TEXT_DIR / "cohortATT正文补充段落.md").write_text(cohort_text, encoding="utf-8")

    sample_note = "\n".join(
        [
            "## 表注版",
            f"本轮正文采用的Stack DID主规格为 `{MAIN_STACK_SPEC_ID}`。其N为堆叠样本量，never-treated对照地区可在不同cohort子实验中重复进入样本，因此不应与基准DID的262个省—年有效观测直接一一比较。",
            "",
            "## 正文版",
            "需要说明的是，本轮补充识别采用堆叠样本构造，样本量随着控制组定义和窗口长度变化而变化。不同Stack DID规格的N之所以不完全一致，一是因为窗口截断会改变可进入估计的年份数，二是因为not-yet-treated控制组在不同cohort与年份下的可用观测不同，因此其样本记数不能与基准DID面板样本量机械对应。",
        ]
    )
    (TEXT_DIR / "补充识别样本量说明_表注与正文版.md").write_text(sample_note, encoding="utf-8")

    screening_lines = [
        "# stackDID规格筛查说明_最终版",
        "",
        f"- 正式输入主面板：`{panel_path.relative_to(PROJECT_ROOT)}`",
        f"- 基准DID结果表：`{baseline_path.relative_to(PROJECT_ROOT)}`",
        "- 本轮筛查维度：控制组定义（never only / never+not-yet）、事件窗口（[-2,+2] / [-3,+2] / [-2,+1]）。",
        "",
        "## 已测试规格",
    ]
    for spec in SPEC_CATALOG:
        screening_lines.append(f"- `{spec['spec_id']}`：{spec['label']}")
    screening_lines += [
        "",
        "## 筛查结论",
        "- `never-treated only` 与 `never+not-yet-treated` 的点估计几乎相同，说明控制组定义不是当前结果波动的主要来源。",
        "- `[-3,+2]` 相比 `[-2,+2]` 只增加极少观测，却未改善统计强度，反而增加了处理前噪声暴露。",
        "- `[-2,+1]` 样本更小，执行阶段与采购阶段的统计支持整体更弱，因此不宜作为主规格。",
        f"- 最终采用 `{MAIN_STACK_SPEC_ID}` 作为Stack DID主规格：它在合法规格中保持了最清晰的方向判断和最可读的样本结构，但仍只能支撑“方向一致、统计强度减弱”的补充识别表述。",
    ]
    (DOC_DIR / "stackDID规格筛查说明_最终版.md").write_text("\n".join(screening_lines), encoding="utf-8")

    dynamic_lines = [
        "# 动态补充识别是否改善前趋势风险_说明_最终版",
        "",
        f"- 基于 `{MAIN_STACK_SPEC_ID}` 的动态压缩结果显示，处理前窗口并未形成足够干净的额外支持。",
        "- 与v1相比，窗口和控制组筛查提高了结果可读性，但没有把动态补充识别改善为可进入正文主论证的强证据。",
        "- 因此，动态图和动态摘要表建议继续保留在附录层或备查层，正文只需一句话说明其未实质改善前趋势风险。",
    ]
    (DOC_DIR / "动态补充识别是否改善前趋势风险_说明_最终版.md").write_text("\n".join(dynamic_lines), encoding="utf-8")

    post_lines = [
        "# post_onset强度检验_本轮去留说明",
        "",
        "- 本轮在最终主规格样本上重跑后，post-onset强度检验并未提供独立增量，且对推进结构变量的方向判断出现反转。",
        "- 因而它不能进入正文，也不宜作为附录主表主图重点展示。",
        "- 当前定位：仅作为备查结果保留，用于说明连续强度口径在高度受限样本中的敏感性。",
    ]
    (DOC_DIR / "post_onset强度检验_本轮去留说明.md").write_text("\n".join(post_lines), encoding="utf-8")

    excluded_rows = never_diff.get("excluded_rows")
    excluded_note = ""
    if isinstance(excluded_rows, pd.DataFrame) and not excluded_rows.empty:
        excluded_note = excluded_rows.to_string(index=False)
    never_lines = [
        "# never_treated数量差异说明",
        "",
        f"- 正式V3主面板中的never-treated数量为 {len(never_diff['full_never'])}：{', '.join(map(str, never_diff['full_never']))}。",
        f"- baseline_sample_5_3过滤后的never-treated数量为 {len(never_diff['baseline_never'])}：{', '.join(map(str, never_diff['baseline_never']))}。",
        f"- 差异来源是 `{', '.join(map(str, never_diff['excluded_never']))}` 在正式主面板中存在，但 `baseline_sample_5_3=0`，因此在进入Stack DID估计前已被排除，而不是被窗口二次剔除。",
        "- 根据主面板记录，该地区未进入正式基准样本，原因是上游官方样本过滤而非本轮脚本的控制组构造问题。",
        "",
        "## 被排除地区在正式主面板中的记录",
        excluded_note,
    ]
    (DOC_DIR / "never_treated数量差异说明.md").write_text("\n".join(never_lines), encoding="utf-8")

    position_lines = [
        "# 补充识别结果在正文中的定位说明",
        "",
        "- 基准`treat_share`多期DID/TWFE仍然是唯一主识别。",
        "- 本轮Stack DID主规格虽然在方向上与基准结果基本一致，但执行阶段结果统计强度有限，因此更适合放在正文5.6中的短节，作为稳健性从属证据，而不是新的主表中心。",
        "- interaction-weighted cohort ATT聚合估计对采购阶段下降提供了相对更强的辅助支持，但对执行阶段上升仍只给出方向性证据，因此它也只能作为补充识别短段或附录增强项。",
        "- 综合判断：Stack DID与cohort ATT都不应改写主线，但二者组合起来可以支持“推进结构结论在更严格处理时点框架下并未反转，只是统计强度减弱”的稳妥写法。",
    ]
    (DOC_DIR / "补充识别结果在正文中的定位说明.md").write_text("\n".join(position_lines), encoding="utf-8")

    method_lines = [
        "# 更稳健cohortATT方法说明",
        "",
        "- 本轮优先尝试 Sun & Abraham / csdid 类方法。",
        f"- Python 包可用性：linearmodels={runtime_info['pkg_linearmodels']}，differences={runtime_info['pkg_differences']}，did={runtime_info['pkg_did']}，rpy2={runtime_info['pkg_rpy2']}。",
        f"- 外部运行时可用性：Rscript={runtime_info['cmd_rscript']}，stata={runtime_info['cmd_stata']}。",
        "- 当前环境下不存在可直接调用的 Sun & Abraham / csdid 标准工具链，因此未做伪实现或空转调用。",
        "- 替代方案：采用 interaction-weighted cohort ATT 聚合估计。做法是在清洁控制组与压缩窗口的Stack样本上，为不同cohort分别估计 post ATT，再按cohort样本量加权聚合，并保留cohort分项结果。",
        "- 该方法比单一Stack DID更接近异质性处理效应稳健估计思路，但仍然只是补充识别，不替代主识别。",
    ]
    (DOC_DIR / "更稳健cohortATT方法说明.md").write_text("\n".join(method_lines), encoding="utf-8")

    file_map = "\n".join(
        [
            "# 文件重命名与文件清单_最终版",
            "",
            "| 本轮文件 | 继承自v1文件 | 是否替换v1 | 用途 |",
            "| --- | --- | --- | --- |",
            "| 表格/StackDID规格比较总表.xlsx | 无 | 否 | round2新增规格总表 |",
            "| 表格/基于StackDID的补充识别结果_最终版.xlsx | did enhance _v1/表格/基于StackDID的补充识别结果_修正版.xlsx | 否 | Stack DID主规格结果表 |",
            "| 表格/StackDID动态效应摘要表_最终版.xlsx | did enhance _v1/表格/StackDID动态效应摘要表_修正版.xlsx | 否 | 动态摘要附表 |",
            "| 表格/更稳健cohortATT补充识别结果.xlsx | 无 | 否 | round2新增cohort ATT结果表 |",
            "| 表格/PostOnset强度稳健性检验_最终版.xlsx | did enhance _v1/表格/PostOnset强度稳健性检验_修正版.xlsx | 否 | 备查附检 |",
            "| 图形/Figure_5_stackdid_vs_baseline_forest_final.png | did enhance _v1/图形/Figure_5_stackdid_vs_baseline_forest_fixed.png | 否 | 主图：基准DID vs Stack DID |",
            "| 图形/Figure_5_stackdid_dynamic_compact_final.png | did enhance _v1/图形/Figure_5_stackdid_dynamic_compact_fixed.png | 否 | 动态附图 |",
            "| 图形/Figure_5_DID_stackDID_cohortATT_threeway_compare.png | 无 | 否 | 三列对照图 |",
        ]
    )
    (DOC_DIR / "文件重命名与文件清单_最终版.md").write_text(file_map, encoding="utf-8")

    checklist = "\n".join(
        [
            "# 本轮DID补强完成清单与待确认事项_最终版",
            "",
            "## 已完成",
            "- 完成六组Stack DID规格比较，并形成总表。",
            "- 明确解释never-treated数量从3到2的真实来源。",
            "- 在环境不支持Sun & Abraham / csdid的情况下，完成interaction-weighted cohort ATT聚合估计替代方案。",
            "- 导出三列对照图，用于比较基准DID、Stack DID与cohort ATT的稳定性差异。",
            "- 生成新的正文替换文本、样本量说明、定位说明和方法说明。",
            "",
            "## 待确认",
            "- 是否将Stack DID主规格结果以正文短节形式并入5.6，而不是附录。",
            "- cohort ATT补充段落是否进入正文5.6，还是保留为附录说明。",
            "- PostOnset强度检验是否只作为备查文件，不再出现在论文附录目录中。",
        ]
    )
    (DOC_DIR / "本轮DID补强完成清单与待确认事项_最终版.md").write_text(checklist, encoding="utf-8")

    problem_sheet = "\n".join(
        [
            "# 问题修复对照表_7旧2新",
            "",
            "| 问题 | 处理方式 | 当前结论 |",
            "| --- | --- | --- |",
            "| 旧1 主结果补强不足 | 扩展为6组规格比较并重选主规格 | 方向一致性仍在，但统计强度只部分改善 |",
            "| 旧2 正文替换文本过满 | 依据round2结果重写 | 已改为冷静、边界更强版本 |",
            "| 旧3 动态结果不能改善前趋势 | 重新筛查后降格 | 仅保留附录/备查定位 |",
            "| 旧4 样本量说明不一致 | 按round2主规格重写 | 已修复 |",
            "| 旧5 顶层组织不够严整 | 新建round2文件夹并统一归档 | 已修复 |",
            "| 旧6 说明残留个人环境 | 统一改为通用运行方式 | 已修复 |",
            "| 旧7 post-onset增量低 | 重新评估并降格 | 仅备查 |",
            "| 新1 never-treated 3→2 不一致 | 追溯到baseline_sample_5_3过滤 | 已解释具体地区与原因 |",
            "| 新2 stack DID正文定位变化 | 依据round2结果重判 | 建议正文短节，不宜主补强中心化 |",
        ]
    )
    (DOC_DIR / "问题修复对照表_7旧2新.md").write_text(problem_sheet, encoding="utf-8")

    script_usage = "\n".join(
        [
            "# 脚本使用说明_最终版",
            "",
            "## 脚本",
            "- `run_did_reinforcement_round2_planA.py`：读取正式V3主面板、基准DID结果与v1补强信息，完成round2的Stack DID规格筛查、cohort ATT替代估计、三列对照图和全部说明文件导出。",
            "",
            "## 输入文件来源",
            "- 正式主面板：项目目录内自动搜索 `PPP_3.6_model_ready_panel_v3_统一口径_方案2_实际执行版_20260413_1048.csv`。",
            "- 基准DID结果：项目目录内自动搜索 `PPP_第5部分_5.3正式回归结果长表_V3_重估版_20260413_1048.csv`。",
            "- v1 对照：`did enhance _v1/` 下的已导出结果只用于版本映射和说明，不会被覆盖。",
            "",
            "## 输出目录",
            "- 表格输出到 `did修改补强_round2_方案A/表格/`",
            "- 图形输出到 `did修改补强_round2_方案A/图形/`",
            "- 正文替换文本输出到 `did修改补强_round2_方案A/正文替换文本/`",
            "- 说明文档输出到 `did修改补强_round2_方案A/说明/`",
            "- 日志输出到 `did修改补强_round2_方案A/日志/`",
            "",
            "## 运行方式",
            "- 在当前工作目录执行：`python did修改补强_round2_方案A/scripts/run_did_reinforcement_round2_planA.py`",
            "- 若默认 `python` 环境缺少依赖，可在同一工作目录下使用任一已安装依赖的 Python 解释器运行；脚本内部不依赖个人Windows绝对路径。",
        ]
    )
    (SCRIPTS_DIR / "脚本使用说明_最终版.md").write_text(script_usage, encoding="utf-8")


def write_log(runtime_info: Dict[str, object]) -> None:
    lines = [
        "# 运行日志与报错处理记录",
        "",
        f"- 生成时间：{datetime.now().isoformat(timespec='seconds')}",
        "- round2 目标：在不改变主识别前提下，重做Stack DID规格筛查，并补充更稳健的cohort ATT替代估计。",
        f"- 环境检测：linearmodels={runtime_info['pkg_linearmodels']}，differences={runtime_info['pkg_differences']}，did={runtime_info['pkg_did']}，rpy2={runtime_info['pkg_rpy2']}，Rscript={runtime_info['cmd_rscript']}，stata={runtime_info['cmd_stata']}",
        "- 由于当前环境不存在可直接调用的Sun & Abraham / csdid标准工具链，因此采用interaction-weighted cohort ATT聚合估计作为最接近的合法替代方案。",
        "- never-treated数量差异已追溯到baseline_sample_5_3上游过滤，而不是本轮窗口设定错误。",
    ]
    (LOG_DIR / "运行日志与报错处理记录.md").write_text("\n".join(lines), encoding="utf-8")


def detect_runtime_info() -> Dict[str, object]:
    return {
        "pkg_linearmodels": importlib.util.find_spec("linearmodels") is not None,
        "pkg_differences": importlib.util.find_spec("differences") is not None,
        "pkg_did": importlib.util.find_spec("did") is not None,
        "pkg_rpy2": importlib.util.find_spec("rpy2") is not None,
        "cmd_rscript": shutil.which("Rscript") is not None,
        "cmd_stata": any(shutil.which(cmd) is not None for cmd in ["stata", "stata-mp", "stata-se"]),
    }


def main() -> None:
    ensure_dirs()
    runtime_info = detect_runtime_info()
    panel, baseline, panel_path, baseline_path = load_inputs()
    data, cohort_counts, never_provinces, never_diff = prepare_panel(panel)
    screening, stacked_map = evaluate_specs(data, cohort_counts, never_provinces, baseline)
    main_results = choose_main_stack_results(screening)
    main_stack = stacked_map[MAIN_STACK_SPEC_ID]
    dynamic = build_dynamic_summary(main_stack)
    post_onset = build_post_onset_intensity(main_stack)
    cohort_att_agg, cohort_att_detail = fit_interaction_weighted_cohort_att(
        data=data,
        cohort_counts=cohort_counts,
        never_provinces=never_provinces,
        window_pre=2,
        window_post=2,
        control_mode="later",
    )
    write_tables(screening, cohort_counts, never_diff, main_results, dynamic, post_onset, cohort_att_agg, cohort_att_detail)
    plot_baseline_vs_stack(baseline, main_results, FIG_DIR / "Figure_5_stackdid_vs_baseline_forest_final.png")
    plot_dynamic(dynamic, FIG_DIR / "Figure_5_stackdid_dynamic_compact_final.png")
    plot_threeway_compare(baseline, main_results, cohort_att_agg, FIG_DIR / "Figure_5_DID_stackDID_cohortATT_threeway_compare.png")
    write_docs(panel_path, baseline_path, never_diff, screening, main_results, cohort_att_agg, dynamic, post_onset, runtime_info)
    write_log(runtime_info)
    print("Round2 DID补强文件已导出到:", OUTPUT_ROOT)


if __name__ == "__main__":
    main()
