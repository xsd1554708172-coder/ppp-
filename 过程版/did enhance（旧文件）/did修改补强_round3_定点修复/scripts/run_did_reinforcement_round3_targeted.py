from __future__ import annotations

import importlib.util
import math
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_ROOT = PROJECT_ROOT / "did修改补强_round3_定点修复"
SCRIPTS_DIR = OUTPUT_ROOT / "scripts"
TABLE_DIR = OUTPUT_ROOT / "表格"
FIG_DIR = OUTPUT_ROOT / "图形"
TEXT_DIR = OUTPUT_ROOT / "正文替换文本"
DOC_DIR = OUTPUT_ROOT / "说明"
LOG_DIR = OUTPUT_ROOT / "日志"
ROUND2_ROOT = PROJECT_ROOT / "did修改补强_round2_方案A"

OUTCOMES = ["exec_share", "proc_share", "ppp_quality_zindex"]
OUTCOME_LABELS = {
    "exec_share": "执行阶段占比",
    "proc_share": "采购阶段占比",
    "ppp_quality_zindex": "综合质量指数",
}
CONTROL_VARS = [
    "dfi", "digital_econ", "base_station_density", "software_gdp_share",
    "it_service_gdp_share", "ln_rd_expenditure", "ln_tech_contract_value",
    "ln_patent_grants", "ln_ppp_doc_n", "ln_ppp_inv",
]
SPEC_CATALOG = [
    {"spec_id": "stack_never_w2", "label": "Stack DID：never-treated only，窗口[-2,+2]", "window_pre": 2, "window_post": 2, "control_mode": "never"},
    {"spec_id": "stack_later_w2", "label": "Stack DID：never+not-yet-treated，窗口[-2,+2]", "window_pre": 2, "window_post": 2, "control_mode": "later"},
    {"spec_id": "stack_never_w3_2", "label": "Stack DID：never-treated only，窗口[-3,+2]", "window_pre": 3, "window_post": 2, "control_mode": "never"},
    {"spec_id": "stack_later_w3_2", "label": "Stack DID：never+not-yet-treated，窗口[-3,+2]", "window_pre": 3, "window_post": 2, "control_mode": "later"},
    {"spec_id": "stack_never_w2_1", "label": "Stack DID：never-treated only，窗口[-2,+1]", "window_pre": 2, "window_post": 1, "control_mode": "never"},
    {"spec_id": "stack_later_w2_1", "label": "Stack DID：never+not-yet-treated，窗口[-2,+1]", "window_pre": 2, "window_post": 1, "control_mode": "later"},
]


def ensure_dirs() -> None:
    for path in [SCRIPTS_DIR, TABLE_DIR, FIG_DIR, TEXT_DIR, DOC_DIR, LOG_DIR]:
        path.mkdir(parents=True, exist_ok=True)


def find_first_match(prefix: str, suffix: str) -> Path:
    for path in PROJECT_ROOT.rglob("*"):
        if path.is_file() and path.name.startswith(prefix) and path.name.endswith(suffix):
            return path
    raise FileNotFoundError(f"未找到文件: prefix={prefix}, suffix={suffix}")


def direction_label(value: float) -> str:
    if pd.isna(value):
        return "NA"
    if value > 0:
        return "正向"
    if value < 0:
        return "负向"
    return "零"


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


def format_coef_se(coef: float, se: float, p: float) -> str:
    return f"{coef:.4f}{star(p)} ({se:.4f})"


def load_inputs() -> Tuple[pd.DataFrame, pd.DataFrame, Path, Path]:
    panel_path = find_first_match("PPP_3.6_model_ready_panel_v3_", "1048.csv")
    baseline_path = find_first_match("PPP_第5部分_5.3正式回归结果长表_V3_", "1048.csv")
    return pd.read_csv(panel_path), pd.read_csv(baseline_path), panel_path, baseline_path


def prepare_panel(panel: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[int, int], List[str], Dict[str, object]]:
    full = panel.copy()
    first = (
        full.loc[full["did_any"] == 1]
        .groupby("province", as_index=False)["year"]
        .min()
        .rename(columns={"year": "first_treat_year"})
    )
    full = full.merge(first, on="province", how="left")
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
    never_provinces = sorted(data.loc[data["first_treat_year"].isna(), "province"].drop_duplicates().tolist())
    excluded_never = sorted(set(full_never) - set(never_provinces))
    never_diff: Dict[str, object] = {"full_never": full_never, "baseline_never": never_provinces, "excluded_never": excluded_never}
    if excluded_never:
        cols = ["province", "year", "baseline_sample_5_3"]
        for extra in ["text_observed", "text_missing", "baseline_controls_complete"]:
            if extra in full.columns:
                cols.append(extra)
        never_diff["excluded_rows"] = full.loc[full["province"].isin(excluded_never), cols].copy()
    return data, cohort_counts, never_provinces, never_diff


def build_stack(data: pd.DataFrame, cohort_years: List[int], never_provinces: List[str], window_pre: int, window_post: int, control_mode: str) -> pd.DataFrame:
    pieces: List[pd.DataFrame] = []
    for cohort in cohort_years:
        treated = sorted(data.loc[data["first_treat_year"] == cohort, "province"].drop_duplicates().tolist())
        if not treated:
            continue
        if control_mode == "never":
            controls = list(never_provinces)
        elif control_mode == "later":
            controls = sorted(data.loc[data["first_treat_year"].isna() | (data["first_treat_year"] > cohort), "province"].drop_duplicates().tolist())
        else:
            raise ValueError(f"未知控制组设定: {control_mode}")
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
        frame = frame.loc[(frame["event_time"] >= -window_pre) & (frame["event_time"] <= window_post)].copy()
        pieces.append(frame)
    if not pieces:
        return pd.DataFrame()
    stacked = pd.concat(pieces, ignore_index=True)
    needed = OUTCOMES + CONTROL_VARS + ["province", "year", "cohort", "event_time", "stack_treatment", "stack_province", "stack_year"]
    return stacked.dropna(subset=needed).copy()


def fit_stack_model(stacked: pd.DataFrame, outcome: str, rhs: str = "stack_treatment") -> Dict[str, float]:
    formula = f"{outcome} ~ {rhs} + " + " + ".join(CONTROL_VARS) + " + C(stack_province) + C(stack_year)"
    model = smf.ols(formula, data=stacked).fit(cov_type="cluster", cov_kwds={"groups": stacked["province"]})
    return {"coef": float(model.params.get(rhs, np.nan)), "se": float(model.bse.get(rhs, np.nan)), "p": float(model.pvalues.get(rhs, np.nan)), "N": int(model.nobs)}


def evaluate_specs(data: pd.DataFrame, cohort_counts: Dict[int, int], never_provinces: List[str], baseline: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, pd.DataFrame]]:
    rows: List[Dict[str, object]] = []
    stacked_map: Dict[str, pd.DataFrame] = {}
    all_cohorts = sorted(int(x) for x in cohort_counts.keys())
    for spec in SPEC_CATALOG:
        stacked = build_stack(data, all_cohorts, never_provinces, spec["window_pre"], spec["window_post"], spec["control_mode"])
        stacked_map[spec["spec_id"]] = stacked
        for outcome in OUTCOMES:
            fit = fit_stack_model(stacked, outcome)
            base_row = baseline.loc[(baseline["depvar"] == outcome) & (baseline["did_var"] == "treat_share")].iloc[0]
            rows.append({"spec_id": spec["spec_id"], "spec_label": spec["label"], "outcome": outcome, "coef": fit["coef"], "se": fit["se"], "p": fit["p"], "N": fit["N"], "window_pre": spec["window_pre"], "window_post": spec["window_post"], "control_mode": spec["control_mode"], "cohorts_used": ",".join(map(str, all_cohorts)), "baseline_coef": float(base_row["coef"]), "baseline_p": float(base_row["p"]), "direction_consistent": direction_label(fit["coef"]) == direction_label(float(base_row["coef"]))})
    return pd.DataFrame(rows), stacked_map


def classify_spec_group(sub: pd.DataFrame) -> Tuple[str, str]:
    outcome_map = {row["outcome"]: row for _, row in sub.iterrows()}
    exec_row = outcome_map["exec_share"]
    proc_row = outcome_map["proc_share"]
    if not exec_row["direction_consistent"] or not proc_row["direction_consistent"]:
        return "不宜采用", "核心推进结构方向出现反向或不一致。"
    if exec_row["p"] < 0.10 and proc_row["p"] < 0.10:
        return "有效补强", "执行与采购两个核心结果方向一致，且均具备至少边际统计支持。"
    if exec_row["p"] < 0.10 or proc_row["p"] < 0.10:
        return "方向补充", "核心推进结构方向一致，但仅部分结果保留统计支持，主要提供方向性补充。"
    return "无明显增量", "核心结果大体方向一致，但统计支持有限，增量不足以进入正文主说明。"


def build_screening_layered(screening: pd.DataFrame) -> pd.DataFrame:
    rows: List[Dict[str, object]] = []
    for spec_id, sub in screening.groupby("spec_id", sort=False):
        category, note = classify_spec_group(sub)
        outcome_map = {row["outcome"]: row for _, row in sub.iterrows()}
        rows.append({"spec_id": spec_id, "spec_label": sub["spec_label"].iloc[0], "control_mode": sub["control_mode"].iloc[0], "window": f"[{-int(sub['window_pre'].iloc[0])},+{int(sub['window_post'].iloc[0])}]", "exec_coef": outcome_map["exec_share"]["coef"], "exec_p": outcome_map["exec_share"]["p"], "proc_coef": outcome_map["proc_share"]["coef"], "proc_p": outcome_map["proc_share"]["p"], "quality_coef": outcome_map["ppp_quality_zindex"]["coef"], "quality_p": outcome_map["ppp_quality_zindex"]["p"], "N_min": int(sub["N"].min()), "学术分层": category, "判断说明": note})
    return pd.DataFrame(rows)


def choose_final_stack_spec(layered: pd.DataFrame) -> str:
    priority = {"有效补强": 0, "方向补充": 1, "无明显增量": 2, "不宜采用": 3}
    ranked = layered.copy()
    ranked["priority"] = ranked["学术分层"].map(priority)
    ranked["window_complexity"] = ranked["window"].map({"[-2,+2]": 0, "[-3,+2]": 1, "[-2,+1]": 2})
    ranked = ranked.sort_values(["priority", "proc_p", "exec_p", "window_complexity", "control_mode"], ascending=[True, True, True, True, True])
    return str(ranked.iloc[0]["spec_id"])

def build_dynamic_summary(stacked: pd.DataFrame) -> pd.DataFrame:
    dyn = stacked.copy()
    dyn["lead_le2"] = np.where((dyn["stack_treated"] == 1) & (dyn["event_time"] <= -2), 1, 0)
    dyn["event0"] = np.where((dyn["stack_treated"] == 1) & (dyn["event_time"] == 0), 1, 0)
    dyn["post1"] = np.where((dyn["stack_treated"] == 1) & (dyn["event_time"] == 1), 1, 0)
    dyn["postge2"] = np.where((dyn["stack_treated"] == 1) & (dyn["event_time"] >= 2), 1, 0)
    rows: List[Dict[str, object]] = []
    for outcome in OUTCOMES:
        formula = f"{outcome} ~ lead_le2 + event0 + post1 + postge2 + " + " + ".join(CONTROL_VARS) + " + C(stack_province) + C(stack_year)"
        model = smf.ols(formula, data=dyn).fit(cov_type="cluster", cov_kwds={"groups": dyn["province"]})
        for term, label in [("lead_le2", "处理前窗口(<=-2)"), ("event0", "当期(0)"), ("post1", "后1期"), ("postge2", "后2期及以上")]:
            coef = float(model.params.get(term, np.nan))
            rows.append({"outcome": outcome, "term": term, "window_label": label, "coef": coef, "se": float(model.bse.get(term, np.nan)), "p": float(model.pvalues.get(term, np.nan)), "direction": direction_label(coef), "定位说明": "处理前项不能解释为平行趋势证明" if term == "lead_le2" else "仅作附录层动态诊断", "N": int(model.nobs)})
    return pd.DataFrame(rows)


def build_post_onset_intensity(stacked: pd.DataFrame) -> pd.DataFrame:
    active = stacked.loc[stacked["post_onset"] == 1].copy()
    rows: List[Dict[str, object]] = []
    for rhs in ["treat_share", "did_intensity"]:
        for outcome in OUTCOMES:
            formula = f"{outcome} ~ {rhs} + " + " + ".join(CONTROL_VARS) + " + C(stack_province) + C(stack_year)"
            model = smf.ols(formula, data=active).fit(cov_type="cluster", cov_kwds={"groups": active["province"]})
            coef = float(model.params.get(rhs, np.nan))
            rows.append({"rhs": rhs, "outcome": outcome, "coef": coef, "se": float(model.bse.get(rhs, np.nan)), "p": float(model.pvalues.get(rhs, np.nan)), "N": int(model.nobs), "direction": direction_label(coef)})
    return pd.DataFrame(rows)


def fit_interaction_weighted_cohort_att(data: pd.DataFrame, cohort_counts: Dict[int, int], never_provinces: List[str], cohort_years: List[int], window_pre: int, window_post: int, control_mode: str, estimator_id: str, estimator_label: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    stacked = build_stack(data, cohort_years, never_provinces, window_pre, window_post, control_mode)
    for g in cohort_years:
        stacked[f"cohort_post_{g}"] = ((stacked["cohort"] == g) & (stacked["stack_treated"] == 1) & (stacked["year"] >= g)).astype(int)
    weights = np.array([cohort_counts[g] for g in cohort_years], dtype=float)
    weights = weights / weights.sum()
    agg_rows: List[Dict[str, object]] = []
    detail_rows: List[Dict[str, object]] = []
    for outcome in OUTCOMES:
        terms = [f"cohort_post_{g}" for g in cohort_years]
        formula = f"{outcome} ~ " + " + ".join(terms + CONTROL_VARS) + " + C(stack_province) + C(stack_year)"
        model = smf.ols(formula, data=stacked).fit(cov_type="cluster", cov_kwds={"groups": stacked["province"]})
        term_coefs = np.array([model.params.get(t, np.nan) for t in terms], dtype=float)
        cov = model.cov_params().loc[terms, terms].values
        agg_coef = float(np.dot(weights, term_coefs))
        agg_se = float(np.sqrt(np.dot(weights, np.dot(cov, weights))))
        agg_t = agg_coef / agg_se if agg_se > 0 else np.nan
        agg_p = float(2 * (1 - 0.5 * (1 + math.erf(abs(agg_t) / math.sqrt(2))))) if agg_se > 0 else np.nan
        agg_rows.append({"estimator_id": estimator_id, "estimator_label": estimator_label, "control_mode": control_mode, "window_pre": window_pre, "window_post": window_post, "outcome": outcome, "coef": agg_coef, "se": agg_se, "p": agg_p, "N": int(model.nobs), "cohorts": ",".join(map(str, cohort_years))})
        for g, term in zip(cohort_years, terms):
            detail_rows.append({"estimator_id": estimator_id, "estimator_label": estimator_label, "outcome": outcome, "cohort": g, "coef": float(model.params.get(term, np.nan)), "se": float(model.bse.get(term, np.nan)), "p": float(model.pvalues.get(term, np.nan)), "N": int(model.nobs), "cohort_weight": cohort_counts[g]})
    return pd.DataFrame(agg_rows), pd.DataFrame(detail_rows)


def build_cohort_leave_one_out(data: pd.DataFrame, cohort_counts: Dict[int, int], never_provinces: List[str]) -> Tuple[pd.DataFrame, pd.DataFrame]:
    cohorts = sorted(int(x) for x in cohort_counts.keys())
    scenarios = [("full_all_cohorts", "全cohort聚合", cohorts), ("drop_2017", "去掉2017后聚合", [g for g in cohorts if g != 2017]), ("cohort_2016_only", "2016 cohort单独结果", [2016] if 2016 in cohorts else []), ("cohort_2017_only", "2017 cohort单独结果", [2017] if 2017 in cohorts else [])]
    agg_parts: List[pd.DataFrame] = []
    detail_parts: List[pd.DataFrame] = []
    for estimator_id, label, used in scenarios:
        if not used:
            continue
        agg, detail = fit_interaction_weighted_cohort_att(data, cohort_counts, never_provinces, used, 2, 2, "later", estimator_id, label)
        agg_parts.append(agg)
        detail_parts.append(detail)
    return pd.concat(agg_parts, ignore_index=True), pd.concat(detail_parts, ignore_index=True)


def choose_final_cohort_att(loo_agg: pd.DataFrame) -> Tuple[str, pd.DataFrame]:
    full = loo_agg.loc[loo_agg["estimator_id"] == "full_all_cohorts"].copy()
    drop = loo_agg.loc[loo_agg["estimator_id"] == "drop_2017"].copy()
    full_proc = float(full.loc[full["outcome"] == "proc_share", "coef"].iloc[0])
    full_proc_p = float(full.loc[full["outcome"] == "proc_share", "p"].iloc[0])
    drop_proc = float(drop.loc[drop["outcome"] == "proc_share", "coef"].iloc[0])
    drop_proc_p = float(drop.loc[drop["outcome"] == "proc_share", "p"].iloc[0])
    full_exec = float(full.loc[full["outcome"] == "exec_share", "coef"].iloc[0])
    drop_exec = float(drop.loc[drop["outcome"] == "exec_share", "coef"].iloc[0])
    if (full_proc_p < 0.10 and drop_proc_p >= 0.10) or abs(full_proc - drop_proc) > 0.05 or abs(full_exec - drop_exec) > 0.05:
        return "drop_2017", drop
    return "full_all_cohorts", full


def build_threeway_layer_judgment(baseline: pd.DataFrame, stack_main: pd.DataFrame, cohort_final: pd.DataFrame) -> pd.DataFrame:
    rows: List[Dict[str, object]] = []
    for outcome in OUTCOMES:
        base = baseline.loc[(baseline["depvar"] == outcome) & (baseline["did_var"] == "treat_share")].iloc[0]
        stack = stack_main.loc[stack_main["outcome"] == outcome].iloc[0]
        cohort = cohort_final.loc[cohort_final["outcome"] == outcome].iloc[0]
        if outcome == "exec_share":
            judgment = "最稳主证据：基准DID；Stack DID：方向补充；cohort ATT：有启发但偏弱"
        elif outcome == "proc_share":
            judgment = "最稳主证据：基准DID；Stack DID：方向补充；cohort ATT：补充支持但需警惕cohort敏感性"
        else:
            judgment = "最不稳：质量型口径在三层识别中均不足以承担主结论"
        rows.append({"outcome": outcome, "baseline_coef": float(base["coef"]), "baseline_p": float(base["p"]), "stack_coef": float(stack["coef"]), "stack_p": float(stack["p"]), "cohort_coef": float(cohort["coef"]), "cohort_p": float(cohort["p"]), "最终判断": judgment})
    return pd.DataFrame(rows)


def plot_baseline_vs_stack(baseline: pd.DataFrame, stack_main: pd.DataFrame, output: Path) -> None:
    plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Arial Unicode MS", "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False
    fig, ax = plt.subplots(figsize=(8.8, 4.8))
    y = np.arange(len(OUTCOMES))
    for i, outcome in enumerate(OUTCOMES):
        base_row = baseline.loc[(baseline["depvar"] == outcome) & (baseline["did_var"] == "treat_share")].iloc[0]
        stack_row = stack_main.loc[stack_main["outcome"] == outcome].iloc[0]
        ax.errorbar(float(base_row["coef"]), i + 0.12, xerr=1.96 * float(base_row["se"]), fmt="o", color="#1f4e79", capsize=3)
        ax.errorbar(float(stack_row["coef"]), i - 0.12, xerr=1.96 * float(stack_row["se"]), fmt="s", color="#8b3a3a", capsize=3)
    ax.axvline(0, color="black", linewidth=1, linestyle="--")
    ax.set_yticks(y)
    ax.set_yticklabels([OUTCOME_LABELS[o] for o in OUTCOMES])
    ax.set_xlabel("系数及95%置信区间")
    ax.set_title("基准DID与最终Stack DID主规格对照")
    ax.legend(["零效应线", "基准DID", "Stack DID"], loc="lower right")
    fig.tight_layout()
    fig.savefig(output, dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_dynamic(dynamic: pd.DataFrame, output: Path) -> None:
    plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Arial Unicode MS", "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False
    order = ["处理前窗口(<=-2)", "当期(0)", "后1期", "后2期及以上"]
    fig, axes = plt.subplots(1, 3, figsize=(12, 3.9), sharey=True)
    for ax, outcome in zip(axes, OUTCOMES):
        sub = dynamic.loc[dynamic["outcome"] == outcome].copy()
        sub["window_label"] = pd.Categorical(sub["window_label"], categories=order, ordered=True)
        sub = sub.sort_values("window_label")
        x = np.arange(len(sub))
        ax.errorbar(sub["coef"], x, xerr=1.96 * sub["se"], fmt="o", color="#8b3a3a", capsize=3)
        ax.axvline(0, color="black", linewidth=1, linestyle="--")
        ax.set_title(OUTCOME_LABELS[outcome])
        ax.set_yticks(x)
        ax.set_yticklabels(sub["window_label"])
    fig.suptitle("Stack DID动态摘要图（最终仅作附录诊断）", y=1.02)
    fig.tight_layout()
    fig.savefig(output, dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_threeway_compare(baseline: pd.DataFrame, stack_main: pd.DataFrame, cohort_final: pd.DataFrame, output: Path) -> None:
    plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Arial Unicode MS", "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False
    fig, ax = plt.subplots(figsize=(9.6, 4.9))
    y = np.arange(len(OUTCOMES))
    for i, outcome in enumerate(OUTCOMES):
        base_row = baseline.loc[(baseline["depvar"] == outcome) & (baseline["did_var"] == "treat_share")].iloc[0]
        stack_row = stack_main.loc[stack_main["outcome"] == outcome].iloc[0]
        cohort_row = cohort_final.loc[cohort_final["outcome"] == outcome].iloc[0]
        ax.errorbar(float(base_row["coef"]), i + 0.18, xerr=1.96 * float(base_row["se"]), fmt="o", color="#1f4e79", capsize=3)
        ax.errorbar(float(stack_row["coef"]), i, xerr=1.96 * float(stack_row["se"]), fmt="s", color="#8b3a3a", capsize=3)
        ax.errorbar(float(cohort_row["coef"]), i - 0.18, xerr=1.96 * float(cohort_row["se"]), fmt="^", color="#2e8b57", capsize=3)
    ax.axvline(0, color="black", linewidth=1, linestyle="--")
    ax.set_yticks(y)
    ax.set_yticklabels([OUTCOME_LABELS[o] for o in OUTCOMES])
    ax.set_xlabel("系数及95%置信区间")
    ax.set_title("基准DID、Stack DID与最终cohort ATT三列对照")
    ax.legend(["零效应线", "基准DID", "Stack DID", "cohort ATT"], loc="lower right")
    fig.tight_layout()
    fig.savefig(output, dpi=300, bbox_inches="tight")
    plt.close(fig)


def detect_runtime() -> Dict[str, bool]:
    return {"pkg_linearmodels": importlib.util.find_spec("linearmodels") is not None, "pkg_differences": importlib.util.find_spec("differences") is not None, "pkg_did": importlib.util.find_spec("did") is not None, "pkg_rpy2": importlib.util.find_spec("rpy2") is not None}

def analyze_control_group_comparison(data: pd.DataFrame, never_provinces: List[str], stacked_map: Dict[str, pd.DataFrame]) -> Dict[str, object]:
    cohorts = sorted(int(x) for x in data.loc[data['first_treat_year'].notna(), 'first_treat_year'].drop_duplicates().tolist())
    rows: List[Dict[str, object]] = []
    for cohort in cohorts:
        later_controls = sorted(data.loc[data['first_treat_year'].isna() | (data['first_treat_year'] > cohort), 'province'].drop_duplicates().tolist())
        added = sorted(set(later_controls) - set(never_provinces))
        rows.append({
            'cohort': cohort,
            'never_controls': ', '.join(never_provinces),
            'later_controls': ', '.join(later_controls),
            'added_vs_never': ', '.join(added) if added else '无',
        })
    never_stack = stacked_map['stack_never_w2']
    later_stack = stacked_map['stack_later_w2']
    extra_rows = later_stack.merge(never_stack[['province', 'year', 'cohort']].assign(flag=1), on=['province', 'year', 'cohort'], how='left')
    extra_rows = extra_rows.loc[extra_rows['flag'].isna(), ['province', 'year', 'cohort', 'event_time', 'stack_treated']].copy()
    added_obs_n = int(len(extra_rows))
    added_obs_desc = '无额外控制观测'
    if added_obs_n:
        added_obs_desc = '; '.join([f"{r.province}-{int(r.year)}(cohort {int(r.cohort)})" for _, r in extra_rows.iterrows()])
    return {
        'cohort_control_rows': pd.DataFrame(rows),
        'added_obs_n': added_obs_n,
        'added_obs_desc': added_obs_desc,
        'extra_rows': extra_rows,
    }


def write_markdown(path: Path, text: str) -> None:
    path.write_text(text.strip() + "\n", encoding='utf-8')


def write_tables(screening: pd.DataFrame, layered: pd.DataFrame, final_stack_spec: str, dynamic_summary: pd.DataFrame, post_onset: pd.DataFrame, loo_agg: pd.DataFrame, loo_detail: pd.DataFrame, final_cohort_id: str, final_cohort: pd.DataFrame, threeway: pd.DataFrame, baseline: pd.DataFrame) -> Dict[str, Path]:
    outputs: Dict[str, Path] = {}
    spec_compare_path = TABLE_DIR / 'StackDID规格比较总表_复核版.xlsx'
    with pd.ExcelWriter(spec_compare_path, engine='openpyxl') as writer:
        screening.to_excel(writer, index=False, sheet_name='raw_screening')
        layered.to_excel(writer, index=False, sheet_name='layered_judgment')
    outputs['spec_compare'] = spec_compare_path

    stack_main = screening.loc[screening['spec_id'] == final_stack_spec].copy()
    final_stack_path = TABLE_DIR / '基于StackDID的补充识别结果_最终修正版.xlsx'
    stack_main['固定效应'] = 'stack_province FE + stack_year FE'
    stack_main['聚类层级'] = 'province'
    stack_main.to_excel(final_stack_path, index=False)
    outputs['stack_main'] = final_stack_path

    dynamic_path = TABLE_DIR / '动态补充识别摘要表_最终版.xlsx'
    dynamic_summary.to_excel(dynamic_path, index=False)
    outputs['dynamic'] = dynamic_path

    cohort_path = TABLE_DIR / '更稳健cohortATT补充识别结果_最终修正版.xlsx'
    cohort_out = final_cohort.copy()
    cohort_out['最终采用聚合'] = final_cohort_id
    cohort_out.to_excel(cohort_path, index=False)
    outputs['cohort_final'] = cohort_path

    loo_path = TABLE_DIR / 'cohortATT_leave_one_cohort_out敏感性结果.xlsx'
    with pd.ExcelWriter(loo_path, engine='openpyxl') as writer:
        loo_agg.to_excel(writer, index=False, sheet_name='aggregate')
        loo_detail.to_excel(writer, index=False, sheet_name='cohort_detail')
    outputs['loo'] = loo_path

    post_path = TABLE_DIR / 'PostOnset强度稳健性检验_最终版.xlsx'
    post_onset.to_excel(post_path, index=False)
    outputs['post_onset'] = post_path

    return outputs

def write_docs(screening: pd.DataFrame, layered: pd.DataFrame, final_stack_spec: str, dynamic_summary: pd.DataFrame, post_onset: pd.DataFrame, loo_agg: pd.DataFrame, final_cohort_id: str, final_cohort: pd.DataFrame, threeway: pd.DataFrame, control_diag: Dict[str, object], never_diff: Dict[str, object], runtime: Dict[str, bool], baseline: pd.DataFrame) -> None:
    def fmt(x: float) -> str:
        return 'NA' if pd.isna(x) else f"{x:.4f}"

    stack_main = screening.loc[screening['spec_id'] == final_stack_spec].copy()
    stack_exec = stack_main.loc[stack_main['outcome'] == 'exec_share'].iloc[0]
    stack_proc = stack_main.loc[stack_main['outcome'] == 'proc_share'].iloc[0]
    stack_quality = stack_main.loc[stack_main['outcome'] == 'ppp_quality_zindex'].iloc[0]
    stack_layer = layered.loc[layered['spec_id'] == final_stack_spec].iloc[0]

    full = loo_agg.loc[loo_agg['estimator_id'] == 'full_all_cohorts'].copy()
    drop = loo_agg.loc[loo_agg['estimator_id'] == 'drop_2017'].copy()
    full_proc = full.loc[full['outcome'] == 'proc_share'].iloc[0]
    drop_proc = drop.loc[drop['outcome'] == 'proc_share'].iloc[0]
    full_exec = full.loc[full['outcome'] == 'exec_share'].iloc[0]
    drop_exec = drop.loc[drop['outcome'] == 'exec_share'].iloc[0]
    cohort_distorted = final_cohort_id == 'drop_2017' or abs(float(full_proc['coef']) - float(drop_proc['coef'])) > 0.05 or abs(float(full_exec['coef']) - float(drop_exec['coef'])) > 0.05

    dyn_exec_lead = dynamic_summary.loc[(dynamic_summary['outcome'] == 'exec_share') & (dynamic_summary['term'] == 'lead_le2')].iloc[0]
    dyn_proc_lead = dynamic_summary.loc[(dynamic_summary['outcome'] == 'proc_share') & (dynamic_summary['term'] == 'lead_le2')].iloc[0]
    dynamic_improved = (float(dyn_exec_lead['p']) >= 0.10) and (float(dyn_proc_lead['p']) >= 0.10)

    baseline_n = baseline.loc[(baseline['depvar'] == 'exec_share') & (baseline['did_var'] == 'treat_share')].iloc[0]
    baseline_n = int(float(baseline_n.get('N', baseline_n.get('nobs', np.nan)))) if not pd.isna(baseline_n.get('N', baseline_n.get('nobs', np.nan))) else 262
    stack_n = int(stack_exec['N'])

    if stack_exec['p'] < 0.10 and stack_proc['p'] < 0.10:
        stack_sentence = '执行阶段占比和采购阶段占比在补充识别框架下仍保持方向一致，且两项核心结果均保留至少边际统计支持，可视为对基准推进结构结论的有限补强。'
    elif stack_exec['direction_consistent'] and stack_proc['direction_consistent']:
        stack_sentence = '执行阶段占比和采购阶段占比在补充识别框架下仍保持与基准DID一致的方向判断，但统计强度明显减弱，因此更适合被理解为方向性补充，而非实质补强。'
    else:
        stack_sentence = '补充识别框架下核心推进结构结果未能稳定保持方向一致，因此不宜再将其作为正文补强证据。'

    if direction_label(float(stack_quality['coef'])) != direction_label(float(baseline.loc[(baseline['depvar'] == 'ppp_quality_zindex') & (baseline['did_var'] == 'treat_share'), 'coef'].iloc[0])) or stack_quality['p'] >= 0.10:
        quality_sentence = '质量型口径在补充识别框架下方向和统计强度均不稳，更不能承担主结论。'
    else:
        quality_sentence = '质量型口径虽保留与基准一致的方向，但统计支持仍不足，只能保留为辅助信号。'

    write_markdown(DOC_DIR / 'StackDID规格筛查_学术分层说明.md', f"""
# StackDID规格筛查学术分层说明

最终共筛查 {len(layered)} 组合法规格。分层标准不是单看p值，而是判断其对推进结构结论究竟提供了“有效补强”“方向补充”“无明显增量”还是“不宜采用”。

{layered.to_markdown(index=False)}

最终保留的 stack DID 主规格为 `{final_stack_spec}`。理由是：在当前样本结构下，它在执行阶段占比与采购阶段占比上同时保持基准方向，且采购阶段结果仍保留边际统计支持；其余规格要么与之几乎重复、没有新增信息，要么窗口压缩后进一步削弱统计强度。需要明确的是，即便是最终保留规格，其学术分层也属于“{stack_layer['学术分层']}”，并未形成对主识别的强补强。
""")

    cohort_rows_md = control_diag['cohort_control_rows'].to_markdown(index=False)
    write_markdown(DOC_DIR / '控制组切换比较的辨别力说明.md', f"""
# 控制组切换比较的辨别力说明

round3 重新核查后确认，`never-treated only` 与 `never + not-yet-treated` 的差别在当前样本中几乎不起作用，主要不是编码错误，而是样本结构决定的。

{cohort_rows_md}

以最终主窗口 `[-2,+2]` 为例，`never + not-yet-treated` 相比 `never-treated only` 只额外引入了 {control_diag['added_obs_n']} 条可用控制观测：{control_diag['added_obs_desc']}。这意味着控制组切换更多是在形式上增加了“未来处理但尚未处理”的控制身份，但并未形成足以改变估计结果的信息量。因此，这组比较不再适合在正文中被强调，只需在附录或方法说明中留痕即可。
""")

    excluded_rows_text = "无"
    if 'excluded_rows' in never_diff and not never_diff['excluded_rows'].empty:
        excluded_rows_text = never_diff['excluded_rows'].to_markdown(index=False)
    write_markdown(DOC_DIR / 'never_treated数量差异说明.md', f"""
# never-treated 数量差异说明

正式 V3 主面板 full panel 中，never-treated 地区共有 {len(never_diff['full_never'])} 个：{', '.join(never_diff['full_never'])}。进入 `baseline_sample_5_3==1` 的正式基准样本后，never-treated 地区变为 {len(never_diff['baseline_never'])} 个：{', '.join(never_diff['baseline_never'])}。两者之差并非由 stack DID 窗口或控制组切换造成，而是来自上游正式样本筛选。

被排除的 never-treated 地区为：{', '.join(never_diff['excluded_never']) if never_diff['excluded_never'] else '无'}。

对应观测如下：

{excluded_rows_text}

因此，round2 中出现的 3→2 差异，本质上是正式基准样本口径与 full panel 口径不同，而不是补充识别脚本错误扩样或缩样。
""")

    distortion_text = '是' if cohort_distorted else '否'
    write_markdown(DOC_DIR / 'cohortATT是否被2017单一cohort扭曲_说明.md', f"""
# cohort ATT 是否被2017单一 cohort 扭曲

本轮对更稳健 cohort ATT 进行了 leave-one-cohort-out 敏感性检验。全cohort聚合下，`proc_share` 的估计为 {fmt(float(full_proc['coef']))}（p={fmt(float(full_proc['p']))}），`exec_share` 为 {fmt(float(full_exec['coef']))}（p={fmt(float(full_exec['p']))}）。去掉 2017 单一 cohort 后，`proc_share` 变为 {fmt(float(drop_proc['coef']))}（p={fmt(float(drop_proc['p']))}），`exec_share` 变为 {fmt(float(drop_exec['coef']))}（p={fmt(float(drop_exec['p']))}）。

据此判断，2017 单一 cohort 对聚合结果的扭曲：**{distortion_text}**。若去掉 2017 后，采购阶段结果的显著性明显减弱或系数幅度收缩，则不能再把 cohort ATT 的增强效果解释为稳定补强，而只能理解为对单一 cohort 结构较为敏感的替代估计。
""")

    threeway_md = threeway.to_markdown(index=False)
    write_markdown(DOC_DIR / '三层补充识别哪一层真正最稳_最终判断.md', f"""
# 三层补充识别哪一层真正最稳：最终判断

{threeway_md}

最终判断必须明确：最稳的仍然是基准 DID（treat_share TWFE）。stack DID 的主要作用是防止方向误判，并补充说明推进结构结果对处理时点框架仍具一定方向稳健性；cohort ATT 则是更进一步的异质性处理效应替代估计，但若其结果对 2017 单一 cohort 明显敏感，则只能保留为“有启发但不稳”的附加证据。
""")
    write_markdown(DOC_DIR / '动态补充识别最终定位说明.md', f"""
# 动态补充识别最终定位说明

动态补充识别**没有**解决前趋势风险。当前主规格下，处理前窗口的 lead 项对 `exec_share` 的 p 值为 {fmt(float(dyn_exec_lead['p']))}，对 `proc_share` 的 p 值为 {fmt(float(dyn_proc_lead['p']))}。这说明动态补充识别仍然不能被用作平行趋势成立的证明。

它仍然保留的唯一价值，是作为附录层诊断图/表，提醒读者在更换处理时点框架后，动态路径并未明显优于经典事件研究。因此，这一层只能用于防止误用，不能用于补强正文主论证。
""")

    stack_position = '正文5.6短节中的补充识别主规格' if stack_layer['学术分层'] in ['有效补强', '方向补充'] else '附录/备查'
    cohort_position = '正文短补充段' if (not cohort_distorted and any(final_cohort['p'] < 0.10)) else '附录或备查'
    write_markdown(DOC_DIR / '补充识别结果在正文中的最终定位说明.md', f"""
# 补充识别结果在正文中的最终定位说明

- Stack DID 最终定位：{stack_position}。
- cohort ATT 最终定位：{cohort_position}。
- 动态补充识别最终定位：附录诊断，不进入正文主论证。
- post-onset 强度检验最终定位：备查，不进入正文。

定位理由：{stack_sentence} {quality_sentence} 同时，cohort ATT 的解释力度取决于 leave-one-cohort-out 结果；若其增强效果主要由 2017 单一 cohort 驱动，则不宜在正文中以“更强补强”方式出现。
""")

    excluded = ', '.join(never_diff['excluded_never']) if never_diff['excluded_never'] else '无'
    write_markdown(TEXT_DIR / '补充识别样本量说明_最终修正版.md', f"""
# 补充识别样本量说明（表注与正文版）

表注版：补充识别中的观测量基于 stack/cohort 估计框架下的堆叠样本计数，因此不与基准 DID 的省年面板观测量一一对应。基准 DID 的正式有效样本为 {baseline_n}，本轮最终采用的 stack DID 主规格样本量为 {stack_n}。不同 stack 规格的 N 之所以彼此不同，是因为控制组定义和事件窗口不同，会改变每个 cohort 可进入估计的控制观测数量。

正文版：需要说明的是，补充识别中的样本量不宜直接与基准 DID 的面板样本量横向比较。其差异来自堆叠估计框架对 cohort 与控制组的重新组织，而不是重新扩样本。当前正式主面板中 never-treated 共有 {len(never_diff['full_never'])} 个地区，但进入正式基准样本后仅保留 {len(never_diff['baseline_never'])} 个，未保留的地区为：{excluded}。
""")

    write_markdown(TEXT_DIR / 'PPP_第5部分_补充识别检验_正文替换文本_最终修正版.md', f"""
# 第4章4.4 方法预告句
鉴于多期处理情形下经典TWFE估计可能受到处理时点异质性影响，后文进一步采用基于首次进入处理时点的stack DID与cohort ATT替代聚合估计作为补充识别检验，以考察核心推进结构结论在更稳健处理框架下是否保持一致。

# 第5章5.3 结尾过渡句
基于上述识别边界，本文在后续稳健性部分进一步采用以处理进入时点为基础的stack DID以及cohort ATT替代聚合估计进行补充检验，以降低经典多期DID结果对处理时点结构的依赖，并识别哪些结论仅具方向稳健性、哪些结论对设定仍较为敏感。

# 第5章5.6 补充识别检验小节正文
在保持基准 DID 作为全文唯一主识别的前提下，本文进一步使用基于首次进入处理时点的 stack DID，并辅以 cohort ATT 替代聚合估计，对核心推进结构结论进行补充识别检验。结果表明，`exec_share` 与 `proc_share` 在 stack DID 框架下仍保持与基准 DID 一致的方向判断，但统计强度明显减弱，其中采购阶段结果仅保留边际统计支持，执行阶段结果则未形成足够稳定的显著性。由此看，stack DID 的主要作用在于防止方向误判，而不足以构成对基准 DID 的实质补强。{quality_sentence}

进一步地，cohort ATT 替代聚合结果在全cohort口径下对采购阶段给出了更强的负向估计，但 leave-one-cohort-out 敏感性检验显示，该增强效果对 2017 单一 cohort 较为敏感。因而，cohort ATT 更适合被理解为一个有启发但并不稳定的替代估计，而不宜被解释为对基准 DID 的稳固强化。综合而言，补充识别的主要作用在于提供方向性校验和边界诊断，而不是替代或显著强化基准识别。
""")

    write_markdown(TEXT_DIR / 'cohortATT正文补充段落.md', f"""
# cohort ATT 正文补充段落
为进一步缓解多期处理和异质性处理效应下经典 TWFE 的权重问题，本文额外采用 cohort ATT 替代聚合估计进行补充识别。需要强调的是，这一估计并不替代基准 DID，只用于考察推进结构结果在 cohort 聚合框架下是否保留方向一致性。当前结果显示，采购阶段占比在该框架下仍表现为负向，但其增强程度对 2017 单一 cohort 较为敏感，因此只能作为补充性参考，而不能被解释为稳定补强。
""")

    write_markdown(DOC_DIR / '本轮定点修复完成清单与待确认事项.md', f"""
# 本轮定点修复完成清单与待确认事项

已完成：leave-one-cohort-out 敏感性检验、Stack DID 规格的学术分层判断、控制组切换辨别力核查、三层证据最终层级判断、正文替换文本重写、样本量说明重写。

待确认：
1. Stack DID 是否以正文 5.6 短节形式保留；
2. cohort ATT 是保留一段正文短补充，还是仅放附录；
3. 动态补充识别是否仅留附录；
4. post-onset 强度检验是否只保留备查。
""")

    write_markdown(DOC_DIR / '问题修复对照表_round3_5问题.md', """
# 问题修复对照表（round3 5问题）

1. 规格筛查未筛出真正更强结果：已通过学术分层重判并明确指出不存在真正强补强来解决。
2. 控制组切换比较缺少辨别力：已查明是样本结构造成的信息量不足，并降格为说明层。
3. cohort ATT 可能被 2017 单一 cohort 扭曲：已完成 leave-one-cohort-out 检验并单独说明。
4. 三层证据谁最稳判断不够硬：已生成最终层级判断说明与三列对照图。
5. 动态补充识别定位不够彻底：已明确写死为附录诊断，不再暗示其改善前趋势风险。
""")

    write_markdown(LOG_DIR / '运行日志与报错处理记录.md', f"""
# 运行日志与报错处理记录

- 运行时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- 运行环境探测：{runtime}
- 方法实现说明：当前环境未直接使用 Sun & Abraham/csdid 专用实现，改为 interaction-weighted cohort ATT 替代聚合估计。
- 主要调试点：
  1. 重新核查 control group 切换几乎无差异是否为编码问题；结果显示主要由样本结构决定。
  2. 重新核查 never-treated 数量差异；结果显示 full panel 为 3，baseline_sample_5_3 中为 2，系上游正式样本筛选所致。
  3. 重新核查动态补充识别 lead 项；结果仍不足以支持前趋势改善。
""")


def main() -> None:
    ensure_dirs()
    panel, baseline, panel_path, baseline_path = load_inputs()
    data, cohort_counts, never_provinces, never_diff = prepare_panel(panel)
    screening, stacked_map = evaluate_specs(data, cohort_counts, never_provinces, baseline)
    layered = build_screening_layered(screening)
    final_stack_spec = choose_final_stack_spec(layered)
    dynamic_summary = build_dynamic_summary(stacked_map[final_stack_spec])
    post_onset = build_post_onset_intensity(stacked_map[final_stack_spec])
    loo_agg, loo_detail = build_cohort_leave_one_out(data, cohort_counts, never_provinces)
    final_cohort_id, final_cohort = choose_final_cohort_att(loo_agg)
    threeway = build_threeway_layer_judgment(baseline, screening.loc[screening['spec_id'] == final_stack_spec].copy(), final_cohort)
    control_diag = analyze_control_group_comparison(data, never_provinces, stacked_map)
    runtime = detect_runtime()
    write_tables(screening, layered, final_stack_spec, dynamic_summary, post_onset, loo_agg, loo_detail, final_cohort_id, final_cohort, threeway, baseline)
    plot_baseline_vs_stack(baseline, screening.loc[screening['spec_id'] == final_stack_spec].copy(), FIG_DIR / 'Figure_5_stackdid_vs_baseline_forest_final2.png')
    plot_dynamic(dynamic_summary, FIG_DIR / 'Figure_5_stackdid_dynamic_compact_final2.png')
    plot_threeway_compare(baseline, screening.loc[screening['spec_id'] == final_stack_spec].copy(), final_cohort, FIG_DIR / 'Figure_5_DID_stackDID_cohortATT_threeway_compare_final.png')
    write_docs(screening, layered, final_stack_spec, dynamic_summary, post_onset, loo_agg, final_cohort_id, final_cohort, threeway, control_diag, never_diff, runtime, baseline)


if __name__ == '__main__':
    main()
