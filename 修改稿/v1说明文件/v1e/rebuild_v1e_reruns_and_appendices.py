from __future__ import annotations

import math
import os
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[3]
OUT_DIR = Path(__file__).resolve().parent

BASELINE_CONTROLS = [
    "dfi",
    "digital_econ",
    "base_station_density",
    "software_gdp_share",
    "it_service_gdp_share",
    "ln_rd_expenditure",
    "ln_tech_contract_value",
    "ln_patent_grants",
]


def find_first(predicate) -> Path:
    for dirpath, _, filenames in os.walk(ROOT):
        for filename in filenames:
            if predicate(filename, Path(dirpath)):
                return Path(dirpath) / filename
    raise FileNotFoundError("No file matched predicate")


def locate_inputs() -> dict[str, Path]:
    return {
        "panel_v3": find_first(
            lambda f, _p: f.startswith("PPP_3.6_model_ready_panel_v3_")
            and f.endswith("20260413_1048.csv")
        ),
        "doc_level_v3": find_first(
            lambda f, _p: f.startswith("PPP_doc_level_variables_v3_DID")
            and f.endswith("0912.csv")
        ),
        "province_year_v3": find_first(
            lambda f, _p: f.startswith("PPP_province_year_variables_v3_DID")
            and f.endswith("0912.csv")
        ),
        "text_pool_1472": find_first(
            lambda f, _p: "1472" in f and f.endswith(".csv")
        ),
        "official_53": find_first(
            lambda f, _p: "5.3" in f and f.endswith("20260413_1048.csv")
        ),
    }


def norm_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


@dataclass
class RegressionResult:
    depvar: str
    spec: str
    n: int
    coef: float
    se: float
    z: float
    p: float
    r2: float


def build_design(
    df: pd.DataFrame,
    depvar: str,
    did_var: str,
    *,
    add_trends: bool = False,
) -> tuple[np.ndarray, np.ndarray, list[str], pd.DataFrame]:
    work = df.copy()
    province_dummies = pd.get_dummies(work["province"], prefix="prov", drop_first=True)
    year_dummies = pd.get_dummies(work["year"].astype(str), prefix="year", drop_first=True)

    x_parts = [
        pd.Series(1.0, index=work.index, name="const"),
        work[[did_var] + BASELINE_CONTROLS].astype(float),
        province_dummies.astype(float),
        year_dummies.astype(float),
    ]

    if add_trends:
        year_trend = (work["year"] - work["year"].min()).astype(float)
        ref_province = sorted(work["province"].unique())[0]
        trend_cols = {}
        for province in sorted(work["province"].unique()):
            if province == ref_province:
                continue
            trend_cols[f"trend_{province}"] = (work["province"] == province).astype(float) * year_trend
        if trend_cols:
            x_parts.append(pd.DataFrame(trend_cols, index=work.index))

    x_df = pd.concat(x_parts, axis=1)
    x = x_df.to_numpy(dtype=float)
    y = work[depvar].to_numpy(dtype=float)
    return x, y, list(x_df.columns), work


def cluster_ols(
    df: pd.DataFrame,
    depvar: str,
    did_var: str,
    *,
    add_trends: bool = False,
) -> RegressionResult:
    x, y, columns, work = build_design(df, depvar, did_var, add_trends=add_trends)
    xtx = x.T @ x
    xtx_inv = np.linalg.pinv(xtx)
    beta = xtx_inv @ (x.T @ y)
    resid = y - x @ beta

    groups = work["province"].astype(str).to_numpy()
    unique_groups = np.unique(groups)
    meat = np.zeros((x.shape[1], x.shape[1]), dtype=float)
    for group in unique_groups:
        mask = groups == group
        xg = x[mask]
        ug = resid[mask]
        xu = xg.T @ ug
        meat += np.outer(xu, xu)

    n, k = x.shape
    g = len(unique_groups)
    correction = (g / (g - 1.0)) * ((n - 1.0) / (n - k)) if g > 1 and n > k else 1.0
    cov = correction * (xtx_inv @ meat @ xtx_inv)
    se = np.sqrt(np.diag(cov))

    idx = columns.index(did_var)
    coef = float(beta[idx])
    se_i = float(se[idx])
    z = coef / se_i
    p = 2.0 * (1.0 - norm_cdf(abs(z)))
    yhat = x @ beta
    sst = float(((y - y.mean()) ** 2).sum())
    ssr = float(((y - yhat) ** 2).sum())
    r2 = 1.0 - ssr / sst if sst > 0 else float("nan")

    return RegressionResult(
        depvar=depvar,
        spec="trend_adjusted" if add_trends else "baseline",
        n=n,
        coef=coef,
        se=se_i,
        z=float(z),
        p=float(p),
        r2=float(r2),
    )


def make_treat_share_outputs(panel: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    appendix_a = panel[
        ["province", "year", "city_n", "treat_share", "post", "did_intensity", "did_any", "baseline_sample_5_3"]
    ].copy()
    appendix_a["treated_city_count_implied"] = appendix_a["treat_share"] * appendix_a["city_n"]
    appendix_a = appendix_a[
        [
            "province",
            "year",
            "city_n",
            "treat_share",
            "treated_city_count_implied",
            "post",
            "did_intensity",
            "did_any",
            "baseline_sample_5_3",
        ]
    ].sort_values(["province", "year"])

    timing_rows = []
    for province, sub in panel.sort_values("year").groupby("province"):
        treated = sub.loc[sub["did_intensity"] > 0, "year"]
        if treated.empty:
            timing_rows.append(
                {
                    "province": province,
                    "first_treatment_year": np.nan,
                    "status": "never_treated_in_current_post_window",
                }
            )
        else:
            timing_rows.append(
                {
                    "province": province,
                    "first_treatment_year": int(treated.iloc[0]),
                    "status": "treated",
                }
            )
    timing = pd.DataFrame(timing_rows).sort_values(["status", "first_treatment_year", "province"])

    exclusions = panel.loc[panel["baseline_sample_5_3"] != 1, ["province", "year", "baseline_controls_complete"] + BASELINE_CONTROLS].copy()
    exclusions["exclusion_reason"] = np.where(
        exclusions["baseline_controls_complete"] == 0,
        "baseline_controls_incomplete",
        "not_in_baseline_sample_5_3",
    )
    missing_cols = []
    for _, row in exclusions.iterrows():
        miss = [col for col in BASELINE_CONTROLS if pd.isna(row[col])]
        missing_cols.append(", ".join(miss) if miss else "")
    exclusions["missing_controls"] = missing_cols
    return appendix_a, timing, exclusions.sort_values(["province", "year"])


def make_sample_flow_outputs(
    text_pool: pd.DataFrame,
    doc_level: pd.DataFrame,
    province_year: pd.DataFrame,
    panel: pd.DataFrame,
) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"step": "full_text_pool", "count": int(len(text_pool)), "source": "PPP_政策文本整合结果_1472篇.csv"},
            {
                "step": "doc_level_did_window",
                "count": int(len(doc_level)),
                "source": "PPP_doc_level_variables_v3_DID主识别窗口_2014_2022_地方样本_实际执行版_20260413_0912.csv",
            },
            {
                "step": "province_year_balanced_window",
                "count": int(len(province_year)),
                "source": "PPP_province_year_variables_v3_DID主识别窗口_方案2_平衡口径_实际执行版_20260413_0912.csv",
            },
            {
                "step": "panel_v3_all_observations",
                "count": int(len(panel)),
                "source": "PPP_3.6_model_ready_panel_v3_统一口径_方案2_实际执行版_20260413_1048.csv",
            },
            {
                "step": "baseline_sample_5_3",
                "count": int(panel["baseline_sample_5_3"].sum()),
                "source": "PPP_3.6_model_ready_panel_v3_统一口径_方案2_实际执行版_20260413_1048.csv::baseline_sample_5_3",
            },
        ]
    )


def run_fresh_reruns(panel: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    base_sample = panel.loc[panel["baseline_sample_5_3"] == 1].copy()
    depvars = ["exec_share", "proc_share", "ppp_quality_zindex"]

    baseline_results = [cluster_ols(base_sample, depvar, "treat_share", add_trends=False) for depvar in depvars]
    trend_results = [cluster_ols(base_sample, depvar, "treat_share", add_trends=True) for depvar in depvars]

    all_rows = []
    for result in baseline_results + trend_results:
        all_rows.append(
            {
                "depvar": result.depvar,
                "spec": result.spec,
                "n": result.n,
                "coef": result.coef,
                "se": result.se,
                "z": result.z,
                "p_norm": result.p,
                "r2": result.r2,
            }
        )

    official_53 = pd.read_csv(INPUTS["official_53"])
    official_main = official_53.loc[official_53["did_var"] == "treat_share", ["depvar", "coef", "se", "p"]].rename(
        columns={"coef": "official_coef", "se": "official_se", "p": "official_p"}
    )
    comparison = pd.DataFrame(all_rows).merge(
        official_main,
        on="depvar",
        how="left",
    )
    comparison["coef_gap_vs_official_53"] = np.where(
        comparison["spec"] == "baseline",
        comparison["coef"] - comparison["official_coef"],
        np.nan,
    )
    comparison["se_gap_vs_official_53"] = np.where(
        comparison["spec"] == "baseline",
        comparison["se"] - comparison["official_se"],
        np.nan,
    )
    comparison["p_gap_vs_official_53"] = np.where(
        comparison["spec"] == "baseline",
        comparison["p_norm"] - comparison["official_p"],
        np.nan,
    )
    return pd.DataFrame(all_rows), comparison


def run_log_ratio(panel: pd.DataFrame) -> tuple[pd.DataFrame, str]:
    base_sample = panel.loc[panel["baseline_sample_5_3"] == 1].copy()
    positive_values = pd.concat(
        [
            base_sample.loc[base_sample["exec_share"] > 0, "exec_share"],
            base_sample.loc[base_sample["proc_share"] > 0, "proc_share"],
        ]
    )
    min_positive = float(positive_values.min())
    continuity = min_positive / 2.0
    c_values = [
        ("half_min_positive", continuity),
        ("min_positive", min_positive),
        ("fixed_0.01", 0.01),
        ("fixed_0.001", 0.001),
    ]

    rows = []
    for c_label, c_value in c_values:
        work = base_sample.copy()
        work["log_ratio_exec_proc"] = np.log((work["exec_share"] + c_value) / (work["proc_share"] + c_value))
        result = cluster_ols(work, "log_ratio_exec_proc", "treat_share", add_trends=False)
        rows.append(
            {
                "depvar": result.depvar,
                "continuity_rule": c_label,
                "c_value": c_value,
                "n": result.n,
                "coef": result.coef,
                "se": result.se,
                "z": result.z,
                "p_norm": result.p,
                "r2": result.r2,
            }
        )

    note = "\n".join(
        [
            "# v1e log-ratio 补充估计说明",
            "",
            f"- 正式样本：`baseline_sample_5_3 == 1`，N = `{int(base_sample.shape[0])}`",
            f"- 最小正份额：`{min_positive:.10f}`",
            f"- 基准连续性修正：`c = {continuity:.10f}`",
            "- 估计框架：与表4相同的 `treat_share + controls + province FE + year FE`，省级聚类，正态近似 `p` 值。",
            "- 作用定位：份额型结果变量的构成性补强，不替代 `treat_share` 多期 DID/TWFE 主识别。",
        ]
    )
    return pd.DataFrame(rows), note


def write_markdown_notes(
    inputs: dict[str, Path],
    sample_flow: pd.DataFrame,
    timing: pd.DataFrame,
    fresh_reruns: pd.DataFrame,
    fresh_compare: pd.DataFrame,
    log_ratio: pd.DataFrame,
    log_note: str,
) -> None:
    def frame_to_markdown(df: pd.DataFrame) -> str:
        headers = [str(col) for col in df.columns]
        rows = []
        for row in df.itertuples(index=False, name=None):
            rendered = []
            for value in row:
                if isinstance(value, float):
                    if math.isnan(value):
                        rendered.append("")
                    else:
                        rendered.append(f"{value:.10f}".rstrip("0").rstrip("."))
                else:
                    rendered.append(str(value))
            rows.append(rendered)
        line1 = "| " + " | ".join(headers) + " |"
        line2 = "| " + " | ".join(["---"] * len(headers)) + " |"
        body = ["| " + " | ".join(r) + " |" for r in rows]
        return "\n".join([line1, line2] + body)

    treat_share_definition = "\n".join(
        [
            "# v1e Appendix A：处理变量定义与重构说明",
            "",
            "## 处理变量精确定义",
            "",
            "- `post_t = 1[t >= 2016]`",
            "- `treat_share_{pt} = treated_city_count_{pt} / city_n_{pt}`",
            "- `did_intensity_{pt} = post_t * treat_share_{pt}`",
            "- `did_any_{pt} = 1(did_intensity_{pt} > 0)`",
            "",
            "## 当前仓库内可直接核实的样本流转",
            "",
        ]
    )
    treat_share_definition += frame_to_markdown(sample_flow)
    treat_share_definition += "\n\n## 当前口径下的处理时点摘要\n\n"
    timing_label = timing["first_treatment_year"].apply(
        lambda x: f"{int(x)}" if pd.notna(x) else "未进入处理"
    )
    timing_counts = (
        timing.assign(first_treatment_year_label=timing_label)
        .groupby("first_treatment_year_label", dropna=False)
        .size()
        .reset_index(name="province_count")
        .rename(columns={"first_treatment_year_label": "first_treatment_year"})
    )
    timing_counts["sort_key"] = timing_counts["first_treatment_year"].apply(
        lambda x: int(x) if x.isdigit() else 999999
    )
    timing_counts = timing_counts.sort_values(["sort_key", "first_treatment_year"]).drop(columns="sort_key")
    treat_share_definition += frame_to_markdown(timing_counts)
    treat_share_definition += "\n\n## 输入文件\n\n"
    treat_share_definition += "\n".join(f"- `{k}`: `{v}`" for k, v in inputs.items())
    (OUT_DIR / "appendix_A_treat_share_definition_tables_20260419.md").write_text(treat_share_definition, encoding="utf-8")

    sample_flow_note = "\n".join(
        [
            "# v1e Appendix C：文本池与样本流转一致性说明",
            "",
            "- `1472` 来自 `PPP_政策文本整合结果_1472篇.csv` 的行数。",
            "- `1307` 来自正式 DID 主识别窗口文档级变量表的行数。",
            "- `288` 来自正式省—年平衡口径变量表的行数。",
            "- `266` 与 `262` 来自正式 V3 model-ready panel 及其 `baseline_sample_5_3` 标记。",
            "- 当前仓库没有显式落地城市级处理名单与原始阈值表，因此本轮 appendix 只把省—年重构写成 manuscript-facing 复核材料，不夸大为完整城市级复现包。",
        ]
    )
    (OUT_DIR / "appendix_C_sample_flow_note_20260419.md").write_text(sample_flow_note, encoding="utf-8")

    rerun_note = "\n".join(
        [
            "# v1e fresh rerun summary",
            "",
            "## 基准与趋势调整型 DID fresh rerun",
            "",
            frame_to_markdown(fresh_compare),
            "",
            "## log-ratio fresh rerun",
            "",
            frame_to_markdown(log_ratio),
            "",
            log_note,
        ]
    )
    (OUT_DIR / "fresh_rerun_summary_20260419.md").write_text(rerun_note, encoding="utf-8")

    appendix_d = "\n".join(
        [
            "# v1e Appendix D：主识别防守结果摘要",
            "",
            frame_to_markdown(fresh_reruns),
            "",
            "## 说明",
            "",
            "- baseline 行是本轮手工 cluster-robust FE 复算；趋势调整型行在同一正式样本上额外加入省份线性时间趋势。",
            "- wild cluster bootstrap 数值未在本轮 fresh rerun 中重跑；正文仍沿用项目既有正式防守结果，并在交付说明中标注 blocker。",
        ]
    )
    (OUT_DIR / "appendix_D_defensive_summary_20260419.md").write_text(appendix_d, encoding="utf-8")

    appendix_e = "\n".join(
        [
            "# v1e Appendix E：处理变量与文本证据线索的来源边界",
            "",
            "- `treat_share` 由城市处理状态向省—年层面聚合而来，进入第 5.2 节与第 5.6 节主识别框架。",
            "- A/B/C/D 维度来自政策文本工程后的省—年聚合变量，只在第 5.4 节承担解释性与边界性功能。",
            "- 两类变量都依托政策文本体系，因此其相关性不能被写成彼此独立的强机制识别。",
            "- 项目级机器学习结果仅用于治理辅助识别，不参与主识别抬升。",
        ]
    )
    (OUT_DIR / "appendix_E_source_boundary_20260419.md").write_text(appendix_e, encoding="utf-8")


if __name__ == "__main__":
    INPUTS = locate_inputs()
    panel_v3 = pd.read_csv(INPUTS["panel_v3"])
    doc_level_v3 = pd.read_csv(INPUTS["doc_level_v3"])
    province_year_v3 = pd.read_csv(INPUTS["province_year_v3"])
    text_pool_1472 = pd.read_csv(INPUTS["text_pool_1472"])

    appendix_a, timing, exclusions = make_treat_share_outputs(panel_v3)
    sample_flow = make_sample_flow_outputs(text_pool_1472, doc_level_v3, province_year_v3, panel_v3)
    fresh_reruns, fresh_compare = run_fresh_reruns(panel_v3)
    log_ratio, log_note = run_log_ratio(panel_v3)

    appendix_a.to_csv(OUT_DIR / "appendix_A_treat_share_reconstruction_20260419.csv", index=False, encoding="utf-8-sig")
    timing.to_csv(OUT_DIR / "appendix_A_province_treatment_timing_20260419.csv", index=False, encoding="utf-8-sig")
    exclusions.to_csv(OUT_DIR / "appendix_A_sample_exclusions_20260419.csv", index=False, encoding="utf-8-sig")
    sample_flow.to_csv(OUT_DIR / "appendix_C_sample_flow_20260419.csv", index=False, encoding="utf-8-sig")
    fresh_reruns.to_csv(OUT_DIR / "fresh_rerun_main_results_20260419.csv", index=False, encoding="utf-8-sig")
    fresh_compare.to_csv(OUT_DIR / "fresh_rerun_vs_official_20260419.csv", index=False, encoding="utf-8-sig")
    log_ratio.to_csv(OUT_DIR / "appendix_B_log_ratio_reestimate_20260419.csv", index=False, encoding="utf-8-sig")
    (OUT_DIR / "appendix_B_log_ratio_note_20260419.md").write_text(log_note, encoding="utf-8")

    write_markdown_notes(
        inputs=INPUTS,
        sample_flow=sample_flow,
        timing=timing,
        fresh_reruns=fresh_reruns,
        fresh_compare=fresh_compare,
        log_ratio=log_ratio,
        log_note=log_note,
    )

    print("WROTE:")
    for name in [
        "appendix_A_treat_share_reconstruction_20260419.csv",
        "appendix_A_province_treatment_timing_20260419.csv",
        "appendix_A_sample_exclusions_20260419.csv",
        "appendix_A_treat_share_definition_tables_20260419.md",
        "appendix_B_log_ratio_reestimate_20260419.csv",
        "appendix_B_log_ratio_note_20260419.md",
        "appendix_C_sample_flow_20260419.csv",
        "appendix_C_sample_flow_note_20260419.md",
        "appendix_D_defensive_summary_20260419.md",
        "appendix_E_source_boundary_20260419.md",
        "fresh_rerun_main_results_20260419.csv",
        "fresh_rerun_vs_official_20260419.csv",
        "fresh_rerun_summary_20260419.md",
    ]:
        print(name)
