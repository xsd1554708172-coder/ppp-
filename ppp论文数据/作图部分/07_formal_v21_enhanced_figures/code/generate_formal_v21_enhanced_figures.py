# -*- coding: utf-8 -*-
from __future__ import annotations

import math
import textwrap
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib.font_manager import fontManager
from matplotlib.gridspec import GridSpec
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

try:
    from PIL import Image, ImageDraw, ImageFont
except Exception:
    Image = None
    ImageDraw = None
    ImageFont = None


CURRENT_FILE = Path(__file__).resolve()
BUNDLE_ROOT = CURRENT_FILE.parents[1]
CHART_DIR = BUNDLE_ROOT / "charts"
META_DIR = BUNDLE_ROOT / "metadata"
PAPER_ROOT = next(parent for parent in CURRENT_FILE.parents if parent.name.startswith("ppp"))

CHART_DIR.mkdir(parents=True, exist_ok=True)
META_DIR.mkdir(parents=True, exist_ok=True)


PALETTE = {
    "navy": "#355C7D",
    "brick": "#8A4F4D",
    "teal": "#4F7D73",
    "gold": "#B08D57",
    "slate": "#687782",
    "light": "#E8ECEF",
    "ink": "#243039",
    "muted": "#98A2AA",
    "grid": "#D4D8DC",
    "accent": "#436E8A",
    "accent2": "#8B6A4E",
}

MODEL_STYLE = {
    "Blending(RF+XGB+LGBM+CATB)": {"color": "#355C7D", "marker": "P"},
    "XGBoost": {"color": "#4F7D73", "marker": "D"},
    "CatBoost": {"color": "#B08D57", "marker": "^"},
    "LightGBM": {"color": "#687782", "marker": "s"},
    "Logistic": {"color": "#8A4F4D", "marker": "o"},
    "RandomForest": {"color": "#AF7A6D", "marker": "v"},
}

OUTCOME_LABELS = {
    "exec_share": "Execution share",
    "proc_share": "Procurement share",
    "ppp_quality_zindex": "Governance quality (Z-index)",
}

TREATMENT_LABELS = {
    "treat_share": "Treat share",
    "did_any": "DID any",
    "did_intensity": "DID intensity",
}

ROBUSTNESS_ORDER = [
    "Baseline TWFE",
    "Alt: DID any",
    "Alt: DID intensity",
    "Lagged controls",
    "Drop edge years",
    "Drop special regions",
    "Doc-count >= 1",
    "PSM-DID",
    "DML",
]

SOURCE_MANIFEST = [
    {
        "figure_id": "Figure_0_official_evidence_architecture",
        "intended_use": "Main text",
        "section": "Intro / Data architecture",
        "official_data_sources": "doc_level_v3_0912; province_year_v3_0912; model_ready_panel_v3_1048; project_risk_v3_1048",
        "design_basis": "Nature Methods overview figure; Gestalt principles; PLOS better figures",
        "literature_basis": "C2 政策信息学综述; A3 PPP政策内容分析; B4 大数据试验区DID论文",
        "boundary_note": "Pure architecture figure, no claim beyond official sample construction",
    },
    {
        "figure_id": "Figure_4X_text_construction_dashboard",
        "intended_use": "Main text",
        "section": "Part 3-4",
        "official_data_sources": "doc_level_v3_0912; province_year_v3_0912",
        "design_basis": "Nature Methods arrows/labels; small-multiple logic; topic dynamics from local reference set",
        "literature_basis": "A3 PPP政策内容分析; C1 BERTopic主题演化; C2 政策文本量化综述",
        "boundary_note": "Descriptive only; documents, coverage, A/B/C/D dynamics, and topic heat strips",
    },
    {
        "figure_id": "Figure_5X_baseline_effect_matrix",
        "intended_use": "Main text",
        "section": "Part 5",
        "official_data_sources": "5.3 baseline DID official long table",
        "design_basis": "Nature Methods uncertainty principles; coefficient-plot conventions",
        "literature_basis": "B4 大数据试验区DID; C3 注册制改革与信息披露",
        "boundary_note": "Only official 5.3 results; no deprecated PCA outcome added back in",
    },
    {
        "figure_id": "Figure_5Y_event_study_dashboard",
        "intended_use": "Main text or appendix",
        "section": "Part 5",
        "official_data_sources": "5.4 event-study official long table",
        "design_basis": "Nature Methods uncertainty display; linked multi-panel layout",
        "literature_basis": "B4 大数据试验区DID; C3 注册制改革与信息披露",
        "boundary_note": "Dynamic display only; explicitly marks lead-term instability",
    },
    {
        "figure_id": "Figure_6X_mechanism_evidence_matrix",
        "intended_use": "Main text",
        "section": "Part 6",
        "official_data_sources": "6.1-6.4 mediator equations; 6.5 chain paths; 6.6 strict mediation; 5.3 baseline TWFE",
        "design_basis": "Evidence scorecard design; uncertainty encoding; restrained path summary",
        "literature_basis": "A4 PPP项目推进; B1 政策一致性机制分解; B5 数字风险治理",
        "boundary_note": "Highlights partial chain evidence and unsupported strict mediation",
    },
    {
        "figure_id": "Figure_8X_robustness_compass",
        "intended_use": "Main text",
        "section": "Part 8",
        "official_data_sources": "5.3 baseline DID; 8.1-8.3 robustness; 8.4 PSM-DID; 8.5 IV screening; 8.6 DML",
        "design_basis": "Compact robustness scorecard; rule-out IV strip",
        "literature_basis": "B4 大数据试验区DID; C3 注册制改革; PLOS PR-vs-ROC paper",
        "boundary_note": "Uses 5.3 baseline anchor to avoid mixing the 5.3 vs 8.1 baseline conflict",
    },
    {
        "figure_id": "Figure_9X_model_frontier_consensus",
        "intended_use": "Appendix first, selective main-text use",
        "section": "Part 9",
        "official_data_sources": "6-model comparison xlsx/csv; per-model importance sheets",
        "design_basis": "scikit-learn PR guidance; Nature Methods legend/layout guidance",
        "literature_basis": "B5 数字风险治理; C4 LLM/文本决策扩展 only as future-facing context",
        "boundary_note": "One condensed ML figure only, to avoid overweighting part 9",
    },
]


def pick_font_family() -> str:
    candidates = [
        "Microsoft YaHei",
        "Noto Sans CJK SC",
        "SimHei",
        "PingFang SC",
        "Arial Unicode MS",
        "DejaVu Sans",
    ]
    available = {font.name for font in fontManager.ttflist}
    for candidate in candidates:
        if candidate in available:
            return candidate
    return "DejaVu Sans"


def configure_style() -> None:
    mpl.rcParams.update(
        {
            "font.family": pick_font_family(),
            "axes.unicode_minus": False,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "axes.edgecolor": PALETTE["grid"],
            "axes.labelcolor": PALETTE["ink"],
            "xtick.color": PALETTE["ink"],
            "ytick.color": PALETTE["ink"],
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "svg.fonttype": "none",
        }
    )
    sns.set_theme(style="whitegrid")


def find_one(pattern: str) -> Path:
    matches = sorted(PAPER_ROOT.rglob(pattern))
    if not matches:
        raise FileNotFoundError(f"Pattern not found: {pattern}")
    return matches[-1]


def save_figure(fig: plt.Figure, stem: str) -> None:
    for ext in ["png", "pdf", "svg"]:
        fig.savefig(CHART_DIR / f"{stem}.{ext}", dpi=320 if ext == "png" else None, bbox_inches="tight")
    plt.close(fig)


def compact_feature_name(feature: str) -> str:
    province_map = {
        "辽宁省": "Liaoning",
        "江西省": "Jiangxi",
        "贵州省": "Guizhou",
        "安徽省": "Anhui",
        "浙江省": "Zhejiang",
        "湖北省": "Hubei",
        "河南省": "Henan",
        "山西省": "Shanxi",
        "广西壮族自治区": "Guangxi",
        "甘肃省": "Gansu",
        "天津市": "Tianjin",
        "黑龙江省": "Heilongjiang",
    }
    term_map = {
        "政府付费": "government-paid",
        "使用者付费": "user-paid",
    }
    if feature.startswith("num__"):
        raw = feature.replace("num__", "")
        mapping = {
            "ln_invest": "ln(investment)",
            "year": "year",
            "risk_text_count": "risk term count",
            "项目概况_len": "project summary length",
            "合作范围_len": "cooperation-scope length",
            "批复意见_len": "approval-text length",
        }
        return mapping.get(raw, raw.replace("_", " "))
    if feature.startswith("cat__"):
        raw = feature.replace("cat__", "")
        raw = raw.replace("所在区域(省)_", "province | ")
        raw = raw.replace("所属行业(一级行业)_", "sector-I | ")
        raw = raw.replace("所属行业(二级行业)_", "sector-II | ")
        raw = raw.replace("运作方式_", "mode | ")
        raw = raw.replace("回报机制_", "payment | ")
        raw = raw.replace("采购方式_", "procurement | ")
        for cn, en in province_map.items():
            raw = raw.replace(cn, en)
        for cn, en in term_map.items():
            raw = raw.replace(cn, en)
        return raw
    return feature


def feature_group(feature: str) -> str:
    if feature.startswith("num__"):
        raw = feature.replace("num__", "")
        if raw.endswith("_len"):
            return "Text length"
        if raw in {"year", "ln_invest", "risk_text_count"}:
            return "Numeric core"
        return "Numeric"
    if "所在区域" in feature:
        return "Province"
    if "所属行业" in feature:
        return "Industry"
    if "运作方式" in feature or "采购方式" in feature or "回报机制" in feature:
        return "Contract design"
    return "Other"


def score_from_coef_pvalue(coef: float, pvalue: float) -> float:
    if pvalue < 0.05:
        return 1.0 if coef > 0 else -1.0
    if pvalue < 0.10:
        return 0.70 if coef > 0 else -0.70
    return 0.28 if coef > 0 else -0.28


def text_from_score(score: float) -> str:
    if score >= 0.95:
        return "+"
    if score <= -0.95:
        return "-"
    if score > 0:
        return "(+)"
    if score < 0:
        return "(-)"
    return "0"


def make_contact_sheet() -> None:
    if Image is None:
        return
    pngs = sorted(path for path in CHART_DIR.glob("*.png") if path.name != "contact_sheet.png")
    if not pngs:
        return

    thumbs = []
    for path in pngs:
        img = Image.open(path).convert("RGB")
        img.thumbnail((1200, 760))
        thumbs.append((path.stem, img))

    cols = 2
    rows = math.ceil(len(thumbs) / cols)
    tile_w, tile_h = 1280, 840
    canvas = Image.new("RGB", (cols * tile_w, rows * tile_h), "white")
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.load_default()

    for idx, (stem, img) in enumerate(thumbs):
        row, col = divmod(idx, cols)
        x0, y0 = col * tile_w, row * tile_h
        canvas.paste(img, (x0 + 40, y0 + 55))
        draw.text((x0 + 40, y0 + 20), stem, fill="black", font=font)

    canvas.save(CHART_DIR / "contact_sheet.png")


def load_formal_data() -> dict[str, object]:
    doc = pd.read_csv(find_one("*doc_level_variables_v3*0912.csv"))
    province_year = pd.read_csv(find_one("*province_year_variables_v3*0912.csv"))
    panel = pd.read_csv(find_one("*model_ready_panel_v3*1048.csv"))
    baseline = pd.read_csv(find_one("*5.3*1048.csv"))
    event = pd.read_csv(find_one("*5.4*1048.csv"))
    mech = pd.read_csv(find_one("*6.1-6.4*.csv"))
    chain = pd.read_csv(find_one("*6.5*.csv"))
    strict = pd.read_csv(find_one("*6.6*.csv"))
    robustness = pd.read_csv(find_one("*8.1-8.3常规稳健性结果长表*1048.csv"))
    psm = pd.read_csv(find_one("*8.4*1048.csv"))
    iv = pd.read_csv(find_one("*8.5*1048.csv"))
    dml = pd.read_csv(find_one("*8.6*1048.csv"))
    project = pd.read_csv(find_one("*project_level_risk_model_data_v3*1048.csv"))

    part9_root = next(path for path in PAPER_ROOT.iterdir() if path.is_dir() and path.name.startswith("02_"))
    results_dir = min([path for path in part9_root.iterdir() if path.is_dir()], key=lambda item: len(item.name))
    result_book = next(path for path in results_dir.iterdir() if path.suffix.lower() == ".xlsx")
    result_sheets = pd.read_excel(result_book, sheet_name=None)
    model_compare = next(
        frame for frame in result_sheets.values()
        if {"AUC", "AP", "F1", "Precision", "Recall", "Accuracy", "model"}.issubset(frame.columns)
    )
    importance_tables = {}
    for sheet_name, frame in result_sheets.items():
        if {"feature", "abs_importance"}.issubset(frame.columns):
            model_name = "Blending(RF+XGB+LGBM+CATB)"
            for candidate in MODEL_STYLE:
                if candidate == "Blending(RF+XGB+LGBM+CATB)":
                    if "Blend" in sheet_name or "Blending" in sheet_name:
                        model_name = candidate
                elif candidate in sheet_name:
                    model_name = candidate
            importance_tables[model_name] = frame[["feature", "abs_importance"]].copy()

    prediction_file = max(
        [path for path in results_dir.iterdir() if path.suffix.lower() == ".csv"],
        key=lambda item: item.stat().st_size,
    )
    predictions = pd.read_csv(prediction_file)

    return {
        "doc": doc,
        "province_year": province_year,
        "panel": panel,
        "baseline": baseline,
        "event": event,
        "mech": mech,
        "chain": chain,
        "strict": strict,
        "robustness": robustness,
        "psm": psm,
        "iv": iv,
        "dml": dml,
        "project": project,
        "model_compare": model_compare,
        "importance_tables": importance_tables,
        "predictions": predictions,
    }


def plot_overview_architecture(data: dict[str, object]) -> None:
    doc = data["doc"]
    province_year = data["province_year"]
    panel = data["panel"]
    project = data["project"]
    baseline = data["baseline"]

    used_n = int(panel["baseline_sample_5_3"].sum()) if "baseline_sample_5_3" in panel.columns else int(baseline["N"].max())

    fig, ax = plt.subplots(figsize=(14, 8))
    ax.axis("off")

    boxes = [
        {"xy": (0.03, 0.59), "w": 0.23, "h": 0.25, "fc": "#F3F7FA", "title": "Policy text corpus", "body": f"Document-level sample\nn = {len(doc):,}\n2014-2022 local policy texts"},
        {"xy": (0.31, 0.59), "w": 0.23, "h": 0.25, "fc": "#F8F6F1", "title": "Province-year text layer", "body": f"Balanced province-year panel\nn = {len(province_year):,}\nA/B/C/D indices + topic shares"},
        {"xy": (0.59, 0.59), "w": 0.23, "h": 0.25, "fc": "#F3F7FA", "title": "Formal DID panel", "body": f"Model-ready panel\nn = {len(panel):,}\nBaseline estimation sample = {used_n:,}"},
        {"xy": (0.31, 0.18), "w": 0.23, "h": 0.25, "fc": "#F8F6F1", "title": "Project risk layer", "body": f"Strict no-leakage project data\nn = {len(project):,}\nStructural risk label only"},
    ]

    for item in boxes:
        x0, y0 = item["xy"]
        box = FancyBboxPatch(
            (x0, y0),
            item["w"],
            item["h"],
            boxstyle="round,pad=0.012,rounding_size=0.015",
            linewidth=1.2,
            edgecolor=PALETTE["grid"],
            facecolor=item["fc"],
        )
        ax.add_patch(box)
        ax.text(x0 + 0.015, y0 + item["h"] - 0.045, item["title"], fontsize=13, fontweight="bold", color=PALETTE["ink"])
        ax.text(x0 + 0.015, y0 + 0.065, item["body"], fontsize=11, color=PALETTE["ink"], va="bottom")

    arrows = [
        ((0.26, 0.715), (0.31, 0.715), "Text aggregation"),
        ((0.54, 0.715), (0.59, 0.715), "TWFE-ready merge"),
        ((0.425, 0.59), (0.425, 0.43), "Risk extension"),
    ]
    for start, end, label in arrows:
        patch = FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=15, linewidth=1.3, color=PALETTE["slate"])
        ax.add_patch(patch)
        ax.text((start[0] + end[0]) / 2, (start[1] + end[1]) / 2 + 0.025, label, ha="center", fontsize=10, color=PALETTE["slate"])

    methods = [
        (0.03, 0.47, "Part 3-4\nCoding, BERTopic,\nA/B/C/D and topic construction"),
        (0.59, 0.47, "Part 5\nTWFE + event-study\n(core writing boundary)"),
        (0.84, 0.59, "Part 6\nMechanism screening\n(partial chain only)"),
        (0.84, 0.36, "Part 8\nRobustness, PSM, DML,\nIV feasibility screen"),
        (0.59, 0.18, "Part 9\nRisk ranking / identification\n(not a new main identification)"),
    ]
    for x, y, text in methods:
        ax.text(
            x,
            y,
            text,
            fontsize=10.5,
            ha="left",
            va="top",
            bbox={"boxstyle": "round,pad=0.35", "facecolor": "white", "edgecolor": PALETTE["grid"]},
        )

    ax.text(0.03, 0.94, "Figure 0. Official evidence architecture under the v21 formal package", fontsize=16, fontweight="bold")
    ax.text(
        0.03,
        0.90,
        "This overview is designed to make the workload and layer-by-layer evidence structure visible without crossing the formal writing boundary.",
        fontsize=11,
        color=PALETTE["slate"],
    )
    ax.text(
        0.03,
        0.05,
        "Data counts come from the currently adopted official entities only: 0912 text-construction files, 1048 formal DID panel/results, and the 1048 strict project-risk table.",
        fontsize=10,
        color=PALETTE["slate"],
    )
    save_figure(fig, "Figure_0_official_evidence_architecture")


def plot_text_construction_dashboard(data: dict[str, object]) -> None:
    doc = data["doc"].copy()
    province_year = data["province_year"].copy()

    doc = doc[doc["year"].notna()].copy()
    doc["year"] = doc["year"].round().astype(int)
    province_year["year"] = province_year["year"].astype(int)

    doc_year = doc.groupby("year").size().reindex(sorted(doc["year"].unique()), fill_value=0)
    coverage = province_year.groupby("year").agg(
        text_coverage=("text_observed", "mean"),
        median_doccount=("doc_count", "median"),
        total_doccount=("doc_count", "sum"),
    )

    topic_cols = [col for col in province_year.columns if col.startswith("topic_") and col.endswith("_share")]
    top_topics = province_year[topic_cols].mean().sort_values(ascending=False).head(10).index.tolist()
    topic_heat = province_year.groupby("year")[top_topics].mean().T
    topic_heat.index = [name.replace("_share", "").replace("topic_", "T") for name in topic_heat.index]

    dim_long = []
    for dim in ["A_idx", "B_idx", "C_idx", "D_idx"]:
        grouped = province_year.groupby("year")[dim]
        frame = pd.DataFrame(
            {
                "year": grouped.mean().index,
                "dimension": dim.replace("_idx", ""),
                "mean": grouped.mean().values,
                "q25": grouped.quantile(0.25).values,
                "q75": grouped.quantile(0.75).values,
            }
        )
        dim_long.append(frame)
    dim_df = pd.concat(dim_long, ignore_index=True)

    dim_colors = {"A": PALETTE["navy"], "B": PALETTE["teal"], "C": PALETTE["gold"], "D": PALETTE["brick"]}

    fig = plt.figure(figsize=(16, 10))
    gs = GridSpec(2, 2, figure=fig, height_ratios=[1.0, 1.25], width_ratios=[1.05, 1.0], hspace=0.24, wspace=0.20)

    ax1 = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[0, 1])
    ax3 = fig.add_subplot(gs[1, 0])
    ax4 = fig.add_subplot(gs[1, 1])

    ax1.bar(doc_year.index, doc_year.values, color=PALETTE["navy"], alpha=0.86)
    ax1.set_title("A. Document throughput in the formal text corpus", loc="left", fontsize=13, fontweight="bold")
    ax1.set_ylabel("Documents")
    ax1.set_xlabel("Year")
    ax1.spines[["top", "right"]].set_visible(False)

    ax2.bar(coverage.index, coverage["total_doccount"], color=PALETTE["light"], edgecolor=PALETTE["grid"], linewidth=1.0, label="Total province-year docs")
    ax2.plot(coverage.index, coverage["median_doccount"], color=PALETTE["brick"], linewidth=2.0, marker="o", label="Median doc_count")
    ax2_twin = ax2.twinx()
    ax2_twin.plot(coverage.index, coverage["text_coverage"], color=PALETTE["teal"], linewidth=2.2, marker="s", label="Text-covered share")
    ax2.set_title("B. Coverage and sample intensity", loc="left", fontsize=13, fontweight="bold")
    ax2.set_xlabel("Year")
    ax2.set_ylabel("Total doc_count")
    ax2_twin.set_ylabel("Covered province-year share")
    ax2_twin.set_ylim(0, 1.05)
    ax2.spines["top"].set_visible(False)
    ax2_twin.spines["top"].set_visible(False)
    handles = [
        Line2D([0], [0], color=PALETTE["light"], lw=8, label="Total province-year docs"),
        Line2D([0], [0], color=PALETTE["brick"], lw=2.2, marker="o", label="Median doc_count"),
        Line2D([0], [0], color=PALETTE["teal"], lw=2.2, marker="s", label="Text-covered share"),
    ]
    ax2.legend(handles=handles, frameon=False, loc="upper left")

    for dim, color in dim_colors.items():
        sub = dim_df[dim_df["dimension"] == dim].sort_values("year")
        ax3.fill_between(sub["year"], sub["q25"], sub["q75"], color=color, alpha=0.10)
        ax3.plot(sub["year"], sub["mean"], color=color, linewidth=2.2, marker="o", label=dim)
    ax3.axhline(0, color=PALETTE["grid"], linewidth=1.0)
    ax3.set_title("C. National A/B/C/D index paths with interquartile bands", loc="left", fontsize=13, fontweight="bold")
    ax3.set_xlabel("Year")
    ax3.set_ylabel("Index value")
    ax3.legend(frameon=False, ncol=4, loc="upper left")
    ax3.spines[["top", "right"]].set_visible(False)

    sns.heatmap(
        topic_heat,
        ax=ax4,
        cmap=sns.light_palette(PALETTE["navy"], as_cmap=True),
        cbar_kws={"label": "Mean topic share"},
        linewidths=0.4,
        linecolor="white",
    )
    ax4.set_title("D. Top-topic heat strip over time", loc="left", fontsize=13, fontweight="bold")
    ax4.set_xlabel("Year")
    ax4.set_ylabel("Topic")

    fig.suptitle("Figure 4X. Text-construction dashboard aligned with the formal 0912 text entities", x=0.05, ha="left", fontsize=16, fontweight="bold")
    fig.text(
        0.05,
        0.02,
        "This dashboard stays descriptive: document throughput, province-year coverage, A/B/C/D evolution, and the most active topic strips. It does not substitute for the DID estimands in Part 5.",
        fontsize=10.5,
        color=PALETTE["slate"],
    )
    save_figure(fig, "Figure_4X_text_construction_dashboard")


def plot_baseline_effect_matrix(data: dict[str, object]) -> None:
    baseline = data["baseline"].copy()
    baseline = baseline[baseline["depvar"].isin(OUTCOME_LABELS) & baseline["did_var"].isin(TREATMENT_LABELS)].copy()

    outcome_order = ["exec_share", "proc_share", "ppp_quality_zindex"]
    did_order = ["treat_share", "did_any", "did_intensity"]

    limits = {}
    for outcome in outcome_order:
        sub = baseline[baseline["depvar"] == outcome]
        lows = sub["coef"] - 1.96 * sub["se"]
        highs = sub["coef"] + 1.96 * sub["se"]
        width = max(abs(lows.min()), abs(highs.max()))
        limits[outcome] = (-width * 1.15, width * 1.15)

    fig = plt.figure(figsize=(14, 7.8))
    gs = GridSpec(len(did_order), len(outcome_order), figure=fig, hspace=0.35, wspace=0.20)

    for row, did_var in enumerate(did_order):
        for col, outcome in enumerate(outcome_order):
            ax = fig.add_subplot(gs[row, col])
            item = baseline[(baseline["did_var"] == did_var) & (baseline["depvar"] == outcome)].iloc[0]
            coef = float(item["coef"])
            se = float(item["se"])
            pvalue = float(item["p"])
            ci_low, ci_high = coef - 1.96 * se, coef + 1.96 * se
            color = PALETTE["navy"] if coef >= 0 else PALETTE["brick"]

            ax.axvline(0, color=PALETTE["grid"], linewidth=1.1)
            ax.plot([ci_low, ci_high], [0, 0], color=color, linewidth=3.0)
            ax.scatter(coef, 0, s=95, color=color, zorder=3, edgecolor="white", linewidth=0.9)
            ax.set_xlim(*limits[outcome])
            ax.set_ylim(-1, 1)
            ax.set_yticks([])
            ax.spines[["top", "right", "left"]].set_visible(False)
            ax.grid(False)
            if row == len(did_order) - 1:
                ax.set_xlabel("Coefficient (95% CI)")
            else:
                ax.set_xticklabels([])
            if row == 0:
                ax.set_title(OUTCOME_LABELS[outcome], fontsize=12.5, fontweight="bold")
            if col == 0:
                ax.text(limits[outcome][0] * 0.98, 0.55, TREATMENT_LABELS[did_var], fontsize=11.5, fontweight="bold", ha="left")

            verdict = "stable" if pvalue < 0.05 else ("borderline" if pvalue < 0.10 else "weak")
            ax.text(
                0.98,
                0.86,
                f"coef = {coef:.3f}\np = {pvalue:.3f}\n{verdict}",
                transform=ax.transAxes,
                ha="right",
                va="top",
                fontsize=9.5,
                bbox={"boxstyle": "round,pad=0.25", "facecolor": "#FAFBFC", "edgecolor": PALETTE["grid"]},
            )

    fig.suptitle("Figure 5X. Baseline-effect matrix from the official 5.3 re-estimated DID table", x=0.05, ha="left", fontsize=16, fontweight="bold")
    fig.text(
        0.05,
        0.03,
        "Treat share is visually separated from DID-any and DID-intensity to preserve the current writing boundary: the stable core finding is about progress structure, not a blanket quality upgrade.",
        fontsize=10.5,
        color=PALETTE["slate"],
    )
    save_figure(fig, "Figure_5X_baseline_effect_matrix")


def plot_event_study_dashboard(data: dict[str, object]) -> None:
    event = data["event"].copy()
    outcome_order = ["exec_share", "proc_share", "ppp_quality_zindex"]
    line_colors = {
        "exec_share": PALETTE["navy"],
        "proc_share": PALETTE["brick"],
        "ppp_quality_zindex": PALETTE["gold"],
    }

    fig = plt.figure(figsize=(14.5, 10))
    gs = GridSpec(len(outcome_order), 2, figure=fig, width_ratios=[3.8, 1.25], hspace=0.34, wspace=0.18)

    for row, outcome in enumerate(outcome_order):
        sub = event[event["outcome"] == outcome].sort_values("event_order").copy()
        ax = fig.add_subplot(gs[row, 0])
        note_ax = fig.add_subplot(gs[row, 1])
        note_ax.axis("off")

        ax.axhline(0, color=PALETTE["grid"], linewidth=1.0)
        ax.axvspan(-0.5, sub["event_order"].max() + 0.2, color=PALETTE["light"], alpha=0.35)
        ax.errorbar(
            sub["event_order"],
            sub["coef"],
            yerr=[sub["coef"] - sub["ci_low"], sub["ci_high"] - sub["coef"]],
            fmt="o-",
            color=line_colors[outcome],
            ecolor=PALETTE["slate"],
            elinewidth=1.0,
            capsize=3,
            linewidth=2.2,
            markersize=5,
        )
        ax.set_xticks(sub["event_order"])
        ax.set_xticklabels(sub["event_time"])
        ax.set_ylabel("Coefficient")
        ax.set_title(OUTCOME_LABELS[outcome], loc="left", fontsize=12.5, fontweight="bold")
        ax.spines[["top", "right"]].set_visible(False)

        lead = sub[sub["event_order"] == -2].iloc[0]
        post_mean = sub[sub["event_order"] >= 0]["coef"].mean()
        post_peak = sub[sub["event_order"] >= 0]["coef"].abs().max()
        lead_flag = "Lead flagged" if lead["p"] < 0.10 else "Lead not flagged"
        note_ax.text(0.0, 0.90, lead_flag, fontsize=12, fontweight="bold", color=PALETTE["brick"] if lead["p"] < 0.10 else PALETTE["teal"])
        note_ax.text(0.0, 0.67, f"lead coef = {lead['coef']:.3f}\nlead p = {lead['p']:.3f}", fontsize=10.5)
        note_ax.text(0.0, 0.42, f"post mean = {post_mean:.3f}\n|peak post| = {post_peak:.3f}", fontsize=10.5)
        note_ax.text(
            0.0,
            0.12,
            "Interpretation rule:\nUse as dynamic display,\nnot as decisive proof\nof parallel trends.",
            fontsize=10.0,
            color=PALETTE["slate"],
            bbox={"boxstyle": "round,pad=0.3", "facecolor": "#FAFBFC", "edgecolor": PALETTE["grid"]},
        )

    fig.suptitle("Figure 5Y. Event-study dashboard with explicit lead-term diagnostics", x=0.05, ha="left", fontsize=16, fontweight="bold")
    fig.text(
        0.05,
        0.02,
        "The right-side notes make the writing boundary visible: for execution share and procurement share, the lead bin is already non-trivial, so this figure supports timing intuition rather than a clean pre-trend claim.",
        fontsize=10.5,
        color=PALETTE["slate"],
    )
    save_figure(fig, "Figure_5Y_event_study_dashboard")


def plot_mechanism_evidence_matrix(data: dict[str, object]) -> None:
    baseline = data["baseline"]
    mech = data["mech"]
    chain = data["chain"]
    strict = data["strict"]

    outcome_order = ["exec_share", "proc_share", "ppp_quality_zindex"]
    row_order = ["Direct TWFE", "A mediator path", "B mediator path", "C mediator path", "D mediator path", "Strict indirect via A"]

    matrix_records = []
    for outcome in outcome_order:
        base_row = baseline[(baseline["depvar"] == outcome) & (baseline["did_var"] == "treat_share")].iloc[0]
        matrix_records.append({"row": "Direct TWFE", "outcome": outcome, "coef": base_row["coef"], "p": base_row["p"]})
        for mediator in ["A_idx", "B_idx", "C_idx", "D_idx"]:
            mech_row = mech[(mech["outcome"] == outcome) & (mech["mediator"] == mediator) & (mech["did_var"] == "treat_share")].iloc[0]
            matrix_records.append({"row": f"{mediator[0]} mediator path", "outcome": outcome, "coef": mech_row["coef_mediator"], "p": mech_row["p_mediator"]})
        strict_row = strict[(strict["outcome"] == outcome) & (strict["mediator"] == "A_idx")].iloc[0]
        matrix_records.append({"row": "Strict indirect via A", "outcome": outcome, "coef": strict_row["indirect_effect_ab"], "p": strict_row["sobel_p"]})

    matrix_df = pd.DataFrame(matrix_records)
    pivot = matrix_df.pivot(index="row", columns="outcome", values="coef").reindex(index=row_order, columns=outcome_order)
    pvals = matrix_df.pivot(index="row", columns="outcome", values="p").reindex(index=row_order, columns=outcome_order)

    chain_focus = []
    path_specs = [("treat → A", ("A_idx", "treat_share")), ("A → B", ("B_idx", "A_idx")), ("B → C", ("C_idx", "B_idx")), ("C → D", ("D_idx", "C_idx"))]
    for label, (dependent, variable) in path_specs:
        row = chain[(chain["dependent"] == dependent) & (chain["variable"] == variable)].iloc[0]
        chain_focus.append({"path": label, "coef": row["coef"], "t": row["t"], "p": row["p"]})
    chain_focus = pd.DataFrame(chain_focus)

    fig = plt.figure(figsize=(15.2, 8.8))
    gs = GridSpec(1, 2, figure=fig, width_ratios=[1.85, 1.0], wspace=0.16)
    ax1 = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[0, 1])

    sns.heatmap(
        pivot,
        ax=ax1,
        cmap=sns.diverging_palette(18, 240, as_cmap=True),
        center=0,
        linewidths=0.7,
        linecolor="white",
        cbar_kws={"label": "Coefficient"},
    )
    max_abs = max(abs(float(value)) for value in pivot.to_numpy().flatten())
    for i, row_name in enumerate(pivot.index):
        for j, outcome in enumerate(pivot.columns):
            coef = float(pivot.loc[row_name, outcome])
            pvalue = float(pvals.loc[row_name, outcome])
            ax1.text(j + 0.5, i + 0.5, f"{coef:.3f}\n(p={pvalue:.3f})", ha="center", va="center", fontsize=9, color="white" if abs(coef) > max_abs * 0.42 else PALETTE["ink"])
    ax1.set_title("A. Outcome-facing mechanism evidence matrix", loc="left", fontsize=13, fontweight="bold")
    ax1.set_xlabel("")
    ax1.set_ylabel("")
    ax1.set_xticklabels([OUTCOME_LABELS[col] for col in pivot.columns], rotation=0)
    ax1.set_yticklabels(pivot.index, rotation=0)

    ax2.axvline(0, color=PALETTE["grid"], linewidth=1.0)
    ax2.axvline(1.65, color=PALETTE["muted"], linewidth=1.0, linestyle="--")
    ax2.axvline(-1.65, color=PALETTE["muted"], linewidth=1.0, linestyle="--")
    y = range(len(chain_focus))
    colors = [PALETTE["navy"] if tval >= 0 else PALETTE["brick"] for tval in chain_focus["t"]]
    ax2.hlines(list(y), 0, chain_focus["t"], color=colors, linewidth=2.2)
    ax2.scatter(chain_focus["t"], list(y), s=110, color=colors, edgecolor="white", linewidth=0.9, zorder=3)
    for idx, row in chain_focus.iterrows():
        ax2.text(row["t"] + (0.1 if row["t"] >= 0 else -0.1), idx + 0.12, f"coef={row['coef']:.3f}\np={row['p']:.3f}", fontsize=8.8, ha="left" if row["t"] >= 0 else "right")
    ax2.set_yticks(list(y))
    ax2.set_yticklabels(chain_focus["path"])
    ax2.invert_yaxis()
    ax2.set_xlabel("t statistic")
    ax2.set_title("B. Chain continuity in comparable evidence units", loc="left", fontsize=13, fontweight="bold")
    ax2.spines[["top", "right"]].set_visible(False)
    ax2.text(
        0.02,
        0.02,
        "Strict mediation via A remains unsupported:\nall Sobel p-values > 0.36 and all bootstrap intervals cross zero.",
        transform=ax2.transAxes,
        fontsize=10.0,
        color=PALETTE["slate"],
        bbox={"boxstyle": "round,pad=0.35", "facecolor": "#FAFBFC", "edgecolor": PALETTE["grid"]},
    )

    fig.suptitle("Figure 6X. Mechanism evidence matrix aligned with the current formal writing boundary", x=0.05, ha="left", fontsize=16, fontweight="bold")
    fig.text(
        0.05,
        0.03,
        "The left panel shows why 'interface-first' must be written weakly; the right panel shows that the A→B link is the main chain break. The figure is built to support the phrase 'direction exists, strict mediation remains limited.'",
        fontsize=10.5,
        color=PALETTE["slate"],
    )
    save_figure(fig, "Figure_6X_mechanism_evidence_matrix")


def plot_robustness_compass(data: dict[str, object]) -> None:
    baseline = data["baseline"]
    robustness = data["robustness"]
    psm = data["psm"]
    iv = data["iv"]
    dml = data["dml"]

    records = []
    for outcome in OUTCOME_LABELS:
        for did_var, label in [("treat_share", "Baseline TWFE"), ("did_any", "Alt: DID any"), ("did_intensity", "Alt: DID intensity")]:
            row = baseline[(baseline["depvar"] == outcome) & (baseline["did_var"] == did_var)].iloc[0]
            records.append({"method": label, "outcome": outcome, "coef": row["coef"], "p": row["p"]})

    robust_map = {
        "lagged_controls": "Lagged controls",
        "drop_extreme_years": "Drop edge years",
        "drop_special_regions": "Drop special regions",
        "text_sample_threshold_doccount_ge1": "Doc-count >= 1",
    }
    for spec, label in robust_map.items():
        subset = robustness[(robustness["spec"] == spec) & (robustness["did_var"] == "treat_share")]
        for _, row in subset.iterrows():
            if row["depvar"] in OUTCOME_LABELS:
                records.append({"method": label, "outcome": row["depvar"], "coef": row["coef"], "p": row["p"]})

    for outcome in OUTCOME_LABELS:
        psm_row = psm[(psm["outcome"] == outcome) & (psm["treatment"] == "treat_share")].iloc[0]
        records.append({"method": "PSM-DID", "outcome": outcome, "coef": psm_row["coef"], "p": psm_row["p"]})
        dml_row = dml[dml["outcome"] == outcome].iloc[0]
        records.append({"method": "DML", "outcome": outcome, "coef": dml_row["dml_coef"], "p": dml_row["dml_pvalue"]})

    robust_df = pd.DataFrame(records)
    robust_df["score"] = robust_df.apply(lambda row: score_from_coef_pvalue(row["coef"], row["p"]), axis=1)
    pivot = robust_df.pivot(index="method", columns="outcome", values="score").reindex(index=ROBUSTNESS_ORDER, columns=list(OUTCOME_LABELS.keys()))
    coef_pivot = robust_df.pivot(index="method", columns="outcome", values="coef").reindex(index=ROBUSTNESS_ORDER, columns=list(OUTCOME_LABELS.keys()))
    iv = iv.sort_values("abs_first_stage_t", ascending=True)

    fig = plt.figure(figsize=(15.4, 8.5))
    gs = GridSpec(1, 2, figure=fig, width_ratios=[1.8, 1.0], wspace=0.18)
    ax1 = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[0, 1])

    sns.heatmap(
        pivot,
        ax=ax1,
        cmap=sns.diverging_palette(18, 240, as_cmap=True),
        center=0,
        vmin=-1.0,
        vmax=1.0,
        linewidths=0.8,
        linecolor="white",
        cbar_kws={"label": "Signed evidence score"},
    )
    for i, method in enumerate(pivot.index):
        for j, outcome in enumerate(pivot.columns):
            score = float(pivot.loc[method, outcome])
            coef = float(coef_pivot.loc[method, outcome])
            ax1.text(j + 0.5, i + 0.5, f"{text_from_score(score)}\n{coef:.2f}", ha="center", va="center", fontsize=9)
    ax1.set_title("A. Robustness compass anchored on the official 5.3 baseline", loc="left", fontsize=13, fontweight="bold")
    ax1.set_xticklabels([OUTCOME_LABELS[col] for col in pivot.columns], rotation=0)
    ax1.set_yticklabels(pivot.index, rotation=0)
    ax1.set_xlabel("")
    ax1.set_ylabel("")

    ax2.barh(iv["candidate_iv"], iv["first_stage_t"], color=PALETTE["accent"], alpha=0.78)
    ax2.axvline(0, color=PALETTE["grid"], linewidth=1.0)
    ax2.axvline(10, color=PALETTE["brick"], linewidth=1.1, linestyle="--", label="rule-of-thumb = 10")
    ax2.set_title("B. IV feasibility screen", loc="left", fontsize=13, fontweight="bold")
    ax2.set_xlabel("First-stage t statistic")
    ax2.spines[["top", "right"]].set_visible(False)
    ax2.legend(frameon=False, loc="lower right")
    ax2.text(
        0.02,
        0.93,
        "All candidates fail the feasibility screen.\nBest case: digital_econ, t = 1.51.",
        transform=ax2.transAxes,
        fontsize=10.0,
        va="top",
        bbox={"boxstyle": "round,pad=0.3", "facecolor": "#FAFBFC", "edgecolor": PALETTE["grid"]},
    )

    fig.suptitle("Figure 8X. Robustness compass under the current formal result boundary", x=0.05, ha="left", fontsize=16, fontweight="bold")
    fig.text(
        0.05,
        0.03,
        "Positive/negative signs in parentheses indicate directional consistency without strong significance. The core message remains narrow: execution and procurement structure survive several checks; quality Z stays directionally positive but unstable.",
        fontsize=10.5,
        color=PALETTE["slate"],
    )
    save_figure(fig, "Figure_8X_robustness_compass")


def plot_model_frontier_consensus(data: dict[str, object]) -> None:
    compare = data["model_compare"].copy()
    importance_tables = data["importance_tables"]
    predictions = data["predictions"]

    compare = compare.sort_values("AUC", ascending=False)
    compare["size"] = 380 + compare["AP"] * 900

    importance_frames = []
    for model, frame in importance_tables.items():
        tmp = frame.copy()
        total = tmp["abs_importance"].abs().sum()
        tmp["norm_importance"] = tmp["abs_importance"] / total if total else 0
        tmp = tmp[["feature", "norm_importance"]].rename(columns={"norm_importance": model})
        importance_frames.append(tmp)

    merged = importance_frames[0]
    for frame in importance_frames[1:]:
        merged = merged.merge(frame, on="feature", how="outer")
    merged = merged.fillna(0.0)
    model_cols = [col for col in merged.columns if col != "feature"]
    merged["mean_importance"] = merged[model_cols].mean(axis=1)
    merged = merged.sort_values("mean_importance", ascending=False).head(12)
    heat = merged.set_index("feature")[model_cols]
    heat.index = [compact_feature_name(feature) for feature in heat.index]
    heat.columns = [column.replace("Blending(RF+XGB+LGBM+CATB)", "Blending") for column in heat.columns]

    fig = plt.figure(figsize=(16, 8.8))
    gs = GridSpec(1, 2, figure=fig, width_ratios=[1.0, 1.55], wspace=0.18)
    ax1 = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[0, 1])

    for _, row in compare.iterrows():
        style = MODEL_STYLE[row["model"]]
        ax1.scatter(row["AUC"], row["Recall"], s=row["size"], color=style["color"], marker=style["marker"], alpha=0.86, edgecolor="white", linewidth=1.0)
        ax1.text(row["AUC"] + 0.0008, row["Recall"] + 0.008, f"{row['model']}\nF1={row['F1']:.3f}", fontsize=9.5, ha="left", va="bottom")
    ax1.set_title("A. Performance frontier (AUC × recall, bubble size = AP)", loc="left", fontsize=13, fontweight="bold")
    ax1.set_xlabel("AUC")
    ax1.set_ylabel("Recall")
    ax1.spines[["top", "right"]].set_visible(False)
    ax1.set_xlim(compare["AUC"].min() - 0.01, compare["AUC"].max() + 0.01)
    ax1.set_ylim(compare["Recall"].min() - 0.06, compare["Recall"].max() + 0.08)
    ax1.text(0.02, 0.05, f"Positive-class prevalence in test set = {predictions['y_true'].mean():.3f}", transform=ax1.transAxes, fontsize=10, color=PALETTE["slate"])

    sns.heatmap(
        heat,
        ax=ax2,
        cmap=sns.light_palette(PALETTE["navy"], as_cmap=True),
        linewidths=0.6,
        linecolor="white",
        cbar_kws={"label": "Normalized importance"},
    )
    ax2.set_title("B. Consensus feature-importance heatmap", loc="left", fontsize=13, fontweight="bold")
    ax2.set_xlabel("")
    ax2.set_ylabel("")
    ax2.set_xticklabels(ax2.get_xticklabels(), rotation=25, ha="right")

    group_color = {
        "Text length": PALETTE["gold"],
        "Numeric core": PALETTE["navy"],
        "Numeric": PALETTE["slate"],
        "Province": PALETTE["brick"],
        "Industry": PALETTE["teal"],
        "Contract design": PALETTE["accent2"],
        "Other": PALETTE["muted"],
    }
    original_features = merged["feature"].tolist()
    for tick_label, raw_feature in zip(ax2.get_yticklabels(), original_features):
        tick_label.set_color(group_color.get(feature_group(raw_feature), PALETTE["ink"]))

    legend_handles = [
        Line2D([0], [0], marker="s", color="w", label=group, markerfacecolor=color, markersize=10)
        for group, color in group_color.items()
        if group in {feature_group(raw) for raw in original_features}
    ]
    ax2.legend(handles=legend_handles, frameon=False, loc="upper left", bbox_to_anchor=(1.02, 1.0), title="Feature group")

    fig.suptitle("Figure 9X. One condensed ML figure for part 9: frontier plus feature consensus", x=0.05, ha="left", fontsize=16, fontweight="bold")
    fig.text(
        0.05,
        0.03,
        "This single dense figure is meant to replace a larger stack of part-9 plots in the paper draft. It preserves the correct boundary: Blending is only slightly ahead on AUC, Logistic dominates on recall, and the task remains project-level structural risk ranking.",
        fontsize=10.5,
        color=PALETTE["slate"],
    )
    save_figure(fig, "Figure_9X_model_frontier_consensus")


def write_manifest() -> None:
    pd.DataFrame(SOURCE_MANIFEST).to_csv(META_DIR / "source_manifest.csv", index=False, encoding="utf-8-sig")


def main() -> None:
    configure_style()
    data = load_formal_data()
    plot_overview_architecture(data)
    plot_text_construction_dashboard(data)
    plot_baseline_effect_matrix(data)
    plot_event_study_dashboard(data)
    plot_mechanism_evidence_matrix(data)
    plot_robustness_compass(data)
    plot_model_frontier_consensus(data)
    write_manifest()
    make_contact_sheet()
    print(f"Generated charts in: {CHART_DIR}")


if __name__ == "__main__":
    main()
