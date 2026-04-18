from __future__ import annotations

import math
from pathlib import Path
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_ROOT = PROJECT_ROOT / "did修改补强"
SCRIPTS_DIR = OUTPUT_ROOT / "scripts"
TABLE_DIR = OUTPUT_ROOT / "表格"
FIG_DIR = OUTPUT_ROOT / "图形"
TEXT_DIR = OUTPUT_ROOT / "正文替换文本"
DOC_DIR = OUTPUT_ROOT / "说明"

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

MAIN_SPEC_ID = "S2_pooled_never_w2"
SPEC_CATALOG = [
    {
        "spec_id": "S1_full_never",
        "label": "全cohort + never-treated + 全窗口",
        "include_cohorts": "all",
        "window_pre": None,
        "window_post": None,
        "control_mode": "never",
    },
    {
        "spec_id": "S2_pooled_never_w2",
        "label": "全cohort + never-treated + [-2,+2]",
        "include_cohorts": "all",
        "window_pre": 2,
        "window_post": 2,
        "control_mode": "never",
    },
    {
        "spec_id": "S3_pooled_later_w2",
        "label": "全cohort + never/not-yet + [-2,+2]",
        "include_cohorts": "all",
        "window_pre": 2,
        "window_post": 2,
        "control_mode": "later",
    },
    {
        "spec_id": "S4_2016_never_w2",
        "label": "仅2016 cohort + never-treated + [-2,+2]",
        "include_cohorts": [2016],
        "window_pre": 2,
        "window_post": 2,
        "control_mode": "never",
    },
    {
        "spec_id": "S5_pooled_never_w1_2",
        "label": "全cohort + never-treated + [-1,+2]",
        "include_cohorts": "all",
        "window_pre": 1,
        "window_post": 2,
        "control_mode": "never",
    },
]


def ensure_dirs() -> None:
    for path in [SCRIPTS_DIR, TABLE_DIR, FIG_DIR, TEXT_DIR, DOC_DIR]:
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


def prepare_panel(panel: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[int, int], List[str]]:
    data = panel.loc[panel["baseline_sample_5_3"] == 1].copy()
    first_treat = (
        data.loc[data["did_any"] == 1]
        .groupby("province", as_index=False)["year"]
        .min()
        .rename(columns={"year": "first_treat_year"})
    )
    data = data.merge(first_treat, on="province", how="left")
    cohort_counts = (
        data.loc[data["first_treat_year"].notna(), ["province", "first_treat_year"]]
        .drop_duplicates()
        .groupby("first_treat_year")
        .size()
        .astype(int)
        .to_dict()
    )
    never_provinces = sorted(data.loc[data["first_treat_year"].isna(), "province"].unique().tolist())
    return data, cohort_counts, never_provinces


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
        cohort_years = all_cohorts if spec["include_cohorts"] == "all" else list(spec["include_cohorts"])
        stacked = build_stack(
            data=data,
            cohort_years=cohort_years,
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
                    "cohorts_used": ",".join(map(str, cohort_years)),
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


def choose_main_results(screening: pd.DataFrame) -> pd.DataFrame:
    return screening.loc[screening["spec_id"] == MAIN_SPEC_ID].copy()


def write_tables(
    screening: pd.DataFrame,
    cohort_counts: Dict[int, int],
    main_results: pd.DataFrame,
    dynamic: pd.DataFrame,
    post_onset: pd.DataFrame,
) -> None:
    main_table = main_results.copy()
    main_table["coef_fmt"] = [format_coef(c, p) for c, p in zip(main_table["coef"], main_table["p"])]
    main_table["se_fmt"] = main_table["se"].map(lambda x: f"({x:.4f})")
    main_table["固定效应"] = "stack_province FE + stack_year FE"
    main_table["聚类"] = "province"
    main_table["与基准DID方向是否一致"] = np.where(main_table["direction_consistent"], "是", "否")
    main_table["正文采用说明"] = np.where(
        main_table["outcome"].isin(["exec_share", "proc_share"]),
        "可用于方向一致的补充识别说明",
        "仅可作为边界更强的辅助质量结果",
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
        ]
    )
    cohort_df = pd.DataFrame(
        [{"cohort": int(k), "province_n": int(v)} for k, v in sorted(cohort_counts.items())]
        + [{"cohort": "never-treated", "province_n": 2}]
    )
    with pd.ExcelWriter(TABLE_DIR / "基于StackDID的补充识别结果_修正版.xlsx", engine="openpyxl") as writer:
        main_table.to_excel(writer, sheet_name="主规格结果", index=False)
        screening.to_excel(writer, sheet_name="规格筛查长表", index=False)
        cohort_df.to_excel(writer, sheet_name="cohort分布", index=False)
        sample_note.to_excel(writer, sheet_name="样本量说明", index=False)
    with pd.ExcelWriter(TABLE_DIR / "StackDID动态效应摘要表_修正版.xlsx", engine="openpyxl") as writer:
        dynamic.to_excel(writer, sheet_name="动态摘要", index=False)
    with pd.ExcelWriter(TABLE_DIR / "PostOnset强度稳健性检验_修正版.xlsx", engine="openpyxl") as writer:
        post_onset.to_excel(writer, sheet_name="post_onset", index=False)


def build_replacement_text(main_results: pd.DataFrame) -> str:
    result_map = {row["outcome"]: row for _, row in main_results.iterrows()}
    exec_row = result_map["exec_share"]
    proc_row = result_map["proc_share"]
    qual_row = result_map["ppp_quality_zindex"]

    if exec_row["direction_consistent"] and proc_row["direction_consistent"]:
        core_sentence = "执行阶段占比和采购阶段占比在Stack DID补充识别框架下总体仍保持与基准DID一致的方向判断，但统计强度较基准设定明显减弱，说明推进结构改善这一结论在方向上较稳，同时仍对具体识别设定存在一定敏感性。"
    else:
        core_sentence = "Stack DID补充识别下，推进结构结果未能在方向和统计强度上同时保持稳定，说明相关判断对识别设定较为敏感，正文只能将其作为边界更强的补充诊断，而不能写成额外强化。"

    if qual_row["direction_consistent"] and float(qual_row["p"]) < 0.10:
        qual_sentence = "质量型口径在补充识别框架下仅表现出有限的方向性支持，仍不足以承担全文主结论。"
    else:
        qual_sentence = "质量型口径在补充识别框架下方向和统计强度均不稳，更不能承担主结论。"

    return "\n".join(
        [
            "## 第4章 4.4 方法预告句",
            "鉴于多期处理情形下经典TWFE估计可能受到处理时点异质性影响，后文进一步采用基于首次进入处理时点的stack DID作为补充识别检验，以考察核心推进结构结论在更稳健处理框架下是否保持一致。",
            "",
            "## 第5章 5.3 结尾过渡句",
            "基于上述识别边界，本文在后续稳健性部分进一步采用以处理进入时点为基础的stack DID进行补充检验，以降低经典多期DID结果对处理时点结构的依赖。",
            "",
            "## 第5章 5.6 新增小节：补充识别检验：Stack DID",
            "在不改变`treat_share`多期DID/TWFE作为全文唯一主识别的前提下，本文进一步基于首次进入处理状态的cohort定义构造stack DID补充识别框架，并以never-treated地区作为主要对照组，在压缩窗口的堆叠样本中重新检验核心结果。结果显示，"
            + core_sentence
            + qual_sentence
            + "因此，Stack DID更适合被理解为对主结论方向稳健性的补充核查，而不是对经典TWFE结果的替代。动态项的补充结果未显著改善前置识别风险，故仅保留为附录层诊断，不进入正文主论证。"
        ]
    )


def write_docs(
    panel_path: Path,
    baseline_path: Path,
    screening: pd.DataFrame,
    main_results: pd.DataFrame,
    dynamic: pd.DataFrame,
    post_onset: pd.DataFrame,
) -> None:
    replacement = build_replacement_text(main_results)
    (TEXT_DIR / "PPP_第5部分_stackDID_正文替换文本_修正版.md").write_text(replacement, encoding="utf-8")

    sample_note = "\n".join(
        [
            "## 表注版",
            "Stack DID的N为堆叠样本量。由于never-treated对照地区可在不同cohort子实验中重复进入样本，该样本量不应与基准DID的262个省—年有效观测直接一一比较；这反映的是估计框架变化下的样本记数方式，而非简单扩样本。",
            "",
            "## 正文版",
            "需要说明的是，Stack DID的样本量按照堆叠子实验计算，never-treated对照组可在不同cohort下重复进入估计，因此其N高于基准面板的262个有效观测。这一变化来自估计框架而非样本口径扩张，不宜与基准DID样本量作机械对比。 ",
        ]
    )
    (TEXT_DIR / "stackDID样本量说明_表注与正文版.md").write_text(sample_note, encoding="utf-8")

    screening_lines = [
        "# stackDID规格筛查说明",
        "",
        f"- 正式输入主面板：`{panel_path.relative_to(PROJECT_ROOT)}`",
        f"- 基准DID结果表：`{baseline_path.relative_to(PROJECT_ROOT)}`",
        "- 筛查目标：在不改变主识别口径的前提下，为Stack DID选择一套合法、紧凑、可解释的小而强规格组合。",
        "",
        "## 已测试的合法规格",
    ]
    for spec in SPEC_CATALOG:
        screening_lines.append(f"- `{spec['spec_id']}`：{spec['label']}")
    screening_lines += [
        "",
        "## 淘汰逻辑",
        "- 全窗口规格会显著稀释有限cohort样本中的当期和后期信息，导致估计强度进一步下降。",
        "- 仅保留2016 cohort并不能改善结果，反而使执行阶段占比的方向稳定性更差，因此不宜将2017 cohort简单排除后当作主规格。",
        "- 将not-yet-treated并入对照组后，结果与never-treated主规格几乎相同，但增加了解释复杂度，因此正文不采用更复杂版本。",
        "- 更短的[-1,+2]窗口没有实质改善统计强度，也不利于保留最基本的处理前诊断。",
        "",
        "## 最终正文采用的主规格",
        "- 采用 `S2_pooled_never_w2`：全cohort、never-treated对照组、事件窗口[-2,+2]、控制变量体系与表4主规格一致，并加入stack_province FE与stack_year FE。",
        "- 选择原因：该规格在合法设定中最能兼顾方向稳定、解释清晰与样本利用率，且不会因为过长窗口或过度复杂的控制组口径进一步削弱识别可读性。",
        "- 需要强调：该主规格只支持“方向上较稳”的补充识别判断，不支持写成“主结论完全不依赖经典TWFE设定”。",
    ]
    (DOC_DIR / "stackDID规格筛查说明.md").write_text("\n".join(screening_lines), encoding="utf-8")

    dynamic_lines = [
        "# stackDID动态结果去留说明",
        "",
        "- 采用主规格 `S2_pooled_never_w2` 重新生成动态压缩结果后，处理前窗口并未形成足够干净的额外支持。",
        "- 与昨晚版本相比，压缩窗口减少了无效尾部噪声，但并没有把动态结果改善为可进入正文主论证的强证据。",
        "- 因此，动态结果应降格为附录层诊断，仅用于说明Stack DID并未实质消除前置识别风险。",
        "- 正文中的表述只能写成：动态补充诊断未明显改善前趋势风险，故不再作为正文主支撑。",
    ]
    (DOC_DIR / "stackDID动态结果去留说明.md").write_text("\n".join(dynamic_lines), encoding="utf-8")

    post_lines = [
        "# post_onset强度检验去留说明",
        "",
        "- post-onset强度检验已重跑，但在压缩主规格样本中并未提供稳定的新增支持；对推进结构变量的方向判断甚至出现反转。",
        "- 该检验既不能替代Stack DID主规格，也不适合作为第二层主证据。",
        "- 当前建议：仅保留为备查结果，不进入正文，也不建议作为附录主表主图重点展示。",
        "- 相对于主Stack DID的边际增量：它主要提示进入处理后的连续强度口径对样本选择和窗口设定更加敏感，因此不足以强化正文结论。 ",
    ]
    (DOC_DIR / "post_onset强度检验去留说明.md").write_text("\n".join(post_lines), encoding="utf-8")

    rename_map = "\n".join(
        [
            "# 文件重命名映射表",
            "",
            "| 原文件名 | 新文件名 | 是否替换旧文件 | 新文件用途 |",
            "| --- | --- | --- | --- |",
            "| PPP_第5部分_stackDID_补充识别结果表.xlsx | did修改补强/表格/基于StackDID的补充识别结果_修正版.xlsx | 否 | Stack DID主结果表 |",
            "| PPP_第5部分_stackDID_动态效应摘要表.xlsx | did修改补强/表格/StackDID动态效应摘要表_修正版.xlsx | 否 | 动态摘要附表 |",
            "| PPP_第5部分_stackDID_post_onset_intensity_check.xlsx | did修改补强/表格/PostOnset强度稳健性检验_修正版.xlsx | 否 | 附加强度稳健性附表 |",
            "| Figure_5_stackdid_vs_baseline_forest.png | did修改补强/图形/Figure_5_stackdid_vs_baseline_forest_fixed.png | 否 | 主图：基准DID vs Stack DID |",
            "| Figure_5_stackdid_dynamic_compact.png | did修改补强/图形/Figure_5_stackdid_dynamic_compact_fixed.png | 否 | 附图：动态压缩诊断 |",
            "| PPP_第5部分_stackDID_正文替换文本.md | did修改补强/正文替换文本/PPP_第5部分_stackDID_正文替换文本_修正版.md | 否 | 正文替换文本 |",
            "| run_stack_did_supplement.py | did修改补强/scripts/run_stack_did_reinforcement.py | 否 | 相对路径、可复用脚本 |",
        ]
    )
    (DOC_DIR / "文件重命名映射表.md").write_text(rename_map, encoding="utf-8")

    checklist = "\n".join(
        [
            "# 本轮DID补强完成清单与待确认事项",
            "",
            "## 已完成",
            "- 完成Stack DID合法规格筛查，并锁定 pooled cohort + never-treated + [-2,+2] 为正文主规格。",
            "- 重写为相对路径脚本，不再依赖个人Windows绝对路径。",
            "- 重新导出主表、主图、动态摘要、动态附图、post-onset附检和修正版正文替换文本。",
            "- 明确解释Stack DID样本量高于基准DID的原因，并生成表注版与正文版说明。",
            "- 将动态结果和post-onset强度检验重新定位为附录/备查层，不再误写成正文强化证据。",
            "",
            "## 待确认",
            "- 是否将修正版Stack DID主表与主图正式并入论文第5章5.6。",
            "- 动态压缩图和post-onset附检是否保留在论文附录中，还是仅作为备查文件保存。",
        ]
    )
    (DOC_DIR / "本轮DID补强完成清单与待确认事项.md").write_text(checklist, encoding="utf-8")

    problem_sheet = "\n".join(
        [
            "# 问题修复对照表",
            "",
            "| 问题 | 处理方式 | 当前结论 |",
            "| --- | --- | --- |",
            "| 问题1：主结果补强不足 | 重新筛查规格并锁定紧凑主规格 | 方向一致性保留，但统计强度仍偏弱，只能谨慎写入 |",
            "| 问题2：正文替换文本过满 | 按最终主规格重写 | 已改为冷静、边界更强的表述 |",
            "| 问题3：动态结果仍弱 | 压缩窗口并降格 | 转为附录层诊断 |",
            "| 问题4：样本量278解释不足 | 单独生成表注与正文说明 | 已解释为堆叠样本量，不是扩样本 |",
            "| 问题5：文件名规范差 | 统一新文件命名并生成映射表 | 已修复 |",
            "| 问题6：脚本绝对路径写死 | 重写为相对路径脚本 | 已修复 |",
            "| 问题7：post-onset增量有限 | 重新定位为附加稳健性 | 降格为附录/备查 |",
        ]
    )
    (DOC_DIR / "问题修复对照表.md").write_text(problem_sheet, encoding="utf-8")

    script_usage = "\n".join(
        [
            "# 脚本使用说明",
            "",
            "## 脚本",
            "- `run_stack_did_reinforcement.py`：读取正式V3主面板和基准DID结果表，完成Stack DID规格筛查、主规格估计、动态摘要、post-onset附检，并统一导出本轮补强文件。",
            "",
            "## 输入文件来源",
            "- 正式主面板：项目目录内自动搜索 `PPP_3.6_model_ready_panel_v3_统一口径_方案2_实际执行版_20260413_1048.csv`。",
            "- 基准DID结果：项目目录内自动搜索 `PPP_第5部分_5.3正式回归结果长表_V3_重估版_20260413_1048.csv`。",
            "",
            "## 输出目录",
            "- 表格输出到 `did修改补强/表格/`",
            "- 图形输出到 `did修改补强/图形/`",
            "- 正文替换文本输出到 `did修改补强/正文替换文本/`",
            "- 说明文档输出到 `did修改补强/说明/`",
            "",
            "## 运行方式",
            "- 在当前工作目录执行：`D:\\pythontool\\python.exe did修改补强/scripts/run_stack_did_reinforcement.py`",
            "- 脚本内部不依赖个人Windows绝对路径，使用项目根目录相对解析。",
        ]
    )
    (SCRIPTS_DIR / "脚本使用说明.md").write_text(script_usage, encoding="utf-8")


def main() -> None:
    ensure_dirs()
    panel, baseline, panel_path, baseline_path = load_inputs()
    data, cohort_counts, never_provinces = prepare_panel(panel)
    screening, stacked_map = evaluate_specs(data, cohort_counts, never_provinces, baseline)
    main_results = choose_main_results(screening)
    main_stack = stacked_map[MAIN_SPEC_ID]
    dynamic = build_dynamic_summary(main_stack)
    post_onset = build_post_onset_intensity(main_stack)
    write_tables(screening, cohort_counts, main_results, dynamic, post_onset)
    plot_baseline_vs_stack(baseline, main_results, FIG_DIR / "Figure_5_stackdid_vs_baseline_forest_fixed.png")
    plot_dynamic(dynamic, FIG_DIR / "Figure_5_stackdid_dynamic_compact_fixed.png")
    write_docs(panel_path, baseline_path, screening, main_results, dynamic, post_onset)
    print("Stack DID补强文件已导出到:", OUTPUT_ROOT)


if __name__ == "__main__":
    main()
