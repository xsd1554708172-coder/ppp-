import os
import numpy as np
import pandas as pd
from scipy import sparse
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    roc_auc_score, f1_score, precision_score, recall_score, accuracy_score,
    roc_curve, precision_recall_curve, average_precision_score,
    confusion_matrix, DetCurveDisplay
)
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from catboost import CatBoostClassifier

from plot_font_setup_cn import setup_chinese_fonts
from model_utils_no_leak import (
    load_config, ensure_output_dir, build_no_leak_target,
    add_text_length_features, select_available_features, split_xy,
    build_preprocess, extract_feature_importance
)


MODEL_ORDER = [
    "Logistic",
    "RandomForest",
    "XGBoost",
    "LightGBM",
    "CatBoost",
    "Blending(RF+XGB+LGBM+CATB)",
]

MODEL_COLORS = {
    "Logistic": "#1f3b73",
    "RandomForest": "#8c564b",
    "XGBoost": "#2a6f97",
    "LightGBM": "#6c757d",
    "CatBoost": "#7a5195",
    "Blending(RF+XGB+LGBM+CATB)": "#b22222",
}

MODEL_LINESTYLES = {
    "Logistic": "-",
    "RandomForest": "--",
    "XGBoost": "-.",
    "LightGBM": ":",
    "CatBoost": (0, (3, 1, 1, 1)),
    "Blending(RF+XGB+LGBM+CATB)": (0, (5, 2)),
}


def _safe_zero_div_metric(func, y_true, y_pred):
    return func(y_true, y_pred, zero_division=0)


class DenseTransformer:
    """将稀疏矩阵安全转为 dense，供 CatBoost 使用。"""
    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return X.toarray() if sparse.issparse(X) else X



def get_cfg_value(cfg, key, default):
    return cfg[key] if key in cfg else default



def prepare_strict_dataset(df, cfg):
    """严格版：全部 6 个模型统一使用 3B 特征集 + 同一 train/test split。"""
    df = build_no_leak_target(df, target_col=cfg["target_col"])
    df, text_len_cols = add_text_length_features(df, cfg["text_length_cols_from"])
    numeric_features = cfg["numeric_features"] + text_len_cols
    categorical_features = cfg["categorical_features_3B"]
    numeric_features, categorical_features = select_available_features(df, numeric_features, categorical_features)

    X_train, X_test, y_train, y_test = split_xy(
        df,
        numeric_features,
        categorical_features,
        cfg["target_col"],
        cfg["test_size"],
        cfg["random_state"],
    )
    preprocess = build_preprocess(numeric_features, categorical_features)
    return {
        "df": df,
        "numeric_features": numeric_features,
        "categorical_features": categorical_features,
        "X_train": X_train,
        "X_test": X_test,
        "y_train": y_train,
        "y_test": y_test,
        "preprocess": preprocess,
    }



def build_model_pipelines(cfg, preprocess):
    catb_params = get_cfg_value(
        cfg,
        "catb_params",
        {"iterations": 300, "learning_rate": 0.05, "depth": 6, "verbose": 0},
    )

    models = {
        "Logistic": Pipeline([
            ("preprocess", preprocess),
            ("model", LogisticRegression(**cfg["logistic_params"])),
        ]),
        "RandomForest": Pipeline([
            ("preprocess", preprocess),
            ("model", RandomForestClassifier(random_state=cfg["random_state"], **cfg["rf_params"])),
        ]),
        "XGBoost": Pipeline([
            ("preprocess", preprocess),
            ("model", XGBClassifier(
                random_state=cfg["random_state"],
                objective="binary:logistic",
                eval_metric="logloss",
                **cfg["xgb_params"],
            )),
        ]),
        "LightGBM": Pipeline([
            ("preprocess", preprocess),
            ("model", LGBMClassifier(random_state=cfg["random_state"], **cfg["lgbm_params"])),
        ]),
        "CatBoost": Pipeline([
            ("preprocess", preprocess),
            ("densify", FunctionTransformer(lambda x: x.toarray() if sparse.issparse(x) else x, validate=False)),
            ("model", CatBoostClassifier(random_state=cfg["random_state"], **catb_params)),
        ]),
    }
    return models



def evaluate_predictions(y_true, proba, threshold=0.5):
    pred = (proba >= threshold).astype(int)
    fpr, tpr, _ = roc_curve(y_true, proba)
    precision_curve, recall_curve, _ = precision_recall_curve(y_true, proba)

    metrics = {
        "AUC": roc_auc_score(y_true, proba),
        "AP": average_precision_score(y_true, proba),
        "F1": _safe_zero_div_metric(f1_score, y_true, pred),
        "Precision": _safe_zero_div_metric(precision_score, y_true, pred),
        "Recall": _safe_zero_div_metric(recall_score, y_true, pred),
        "Accuracy": accuracy_score(y_true, pred),
        "positive_rate_test": float(np.mean(y_true)),
        "test_n": int(len(y_true)),
    }
    roc_df = pd.DataFrame({"fpr": fpr, "tpr": tpr})
    pr_df = pd.DataFrame({"precision": precision_curve, "recall": recall_curve})
    return metrics, roc_df, pr_df, pred



def aggregate_blending_importance(importance_tables, base_weights=None, topn=20):
    """对 RF/XGB/LGBM/CATB 的重要性做归一化加权平均，作为 Blending 近似重要性。"""
    base_names = ["RandomForest", "XGBoost", "LightGBM", "CatBoost"]
    if base_weights is None:
        base_weights = {name: 1.0 for name in base_names}

    frames = []
    total_w = 0.0
    for name in base_names:
        if name not in importance_tables:
            continue
        df_imp = importance_tables[name].copy()
        if "feature" not in df_imp.columns or "abs_importance" not in df_imp.columns:
            continue
        w = float(base_weights.get(name, 1.0))
        total_w += w
        s = df_imp["abs_importance"].astype(float)
        norm = s / s.sum() if s.sum() > 0 else s
        tmp = pd.DataFrame({
            "feature": df_imp["feature"].astype(str),
            f"imp_{name}": norm * w,
        })
        frames.append(tmp)

    if not frames:
        return pd.DataFrame(columns=["feature", "abs_importance"])

    out = frames[0]
    for frame in frames[1:]:
        out = out.merge(frame, on="feature", how="outer")
    imp_cols = [c for c in out.columns if c.startswith("imp_")]
    out[imp_cols] = out[imp_cols].fillna(0.0)
    denom = total_w if total_w > 0 else len(imp_cols)
    out["abs_importance"] = out[imp_cols].sum(axis=1) / denom
    out = out.sort_values("abs_importance", ascending=False).reset_index(drop=True)
    return out[["feature", "abs_importance"]].head(topn)



def fit_and_evaluate_strict_models(df, cfg):
    print("=" * 68)
    print("开始运行严格版 6 模型比较（统一 3B 特征集 + 同一 train/test split）")
    print("=" * 68)

    data = prepare_strict_dataset(df, cfg)
    models = build_model_pipelines(cfg, data["preprocess"])

    X_train = data["X_train"]
    X_test = data["X_test"]
    y_train = data["y_train"]
    y_test = data["y_test"]

    results = []
    roc_points = {}
    pr_points = {}
    fitted = {}
    importance_tables = {}

    for name in ["Logistic", "RandomForest", "XGBoost", "LightGBM", "CatBoost"]:
        print(f"  训练模型: {name}")
        pipe = models[name]
        pipe.fit(X_train, y_train)
        proba = pipe.predict_proba(X_test)[:, 1]
        metrics, roc_df, pr_df, pred = evaluate_predictions(y_test, proba)
        metrics["model"] = name
        metrics["train_n"] = int(len(X_train))
        results.append(metrics)
        roc_points[name] = roc_df
        pr_points[name] = pr_df
        fitted[name] = {"pipeline": pipe, "proba": proba, "pred": pred}
        try:
            importance_tables[name] = extract_feature_importance(pipe, 20)
        except Exception:
            importance_tables[name] = pd.DataFrame(columns=["feature", "abs_importance"])
        print(f"    AUC: {metrics['AUC']:.4f}, AP: {metrics['AP']:.4f}, F1: {metrics['F1']:.4f}")

    print("  训练模型: Blending(RF+XGB+LGBM+CATB)")
    blend_weights = get_cfg_value(
        cfg,
        "blend_weights",
        {"RandomForest": 1.0, "XGBoost": 1.0, "LightGBM": 1.0, "CatBoost": 1.0},
    )
    weight_sum = sum(float(blend_weights.get(k, 0.0)) for k in ["RandomForest", "XGBoost", "LightGBM", "CatBoost"])
    if weight_sum <= 0:
        raise ValueError("blend_weights 的权重和必须大于 0。")

    blend_proba = (
        float(blend_weights.get("RandomForest", 0.0)) * fitted["RandomForest"]["proba"]
        + float(blend_weights.get("XGBoost", 0.0)) * fitted["XGBoost"]["proba"]
        + float(blend_weights.get("LightGBM", 0.0)) * fitted["LightGBM"]["proba"]
        + float(blend_weights.get("CatBoost", 0.0)) * fitted["CatBoost"]["proba"]
    ) / weight_sum

    blend_metrics, blend_roc_df, blend_pr_df, blend_pred = evaluate_predictions(y_test, blend_proba)
    blend_metrics["model"] = "Blending(RF+XGB+LGBM+CATB)"
    blend_metrics["train_n"] = int(len(X_train))
    results.append(blend_metrics)
    roc_points["Blending(RF+XGB+LGBM+CATB)"] = blend_roc_df
    pr_points["Blending(RF+XGB+LGBM+CATB)"] = blend_pr_df
    fitted["Blending(RF+XGB+LGBM+CATB)"] = {"pipeline": None, "proba": blend_proba, "pred": blend_pred}
    importance_tables["Blending(RF+XGB+LGBM+CATB)"] = aggregate_blending_importance(importance_tables, blend_weights, topn=20)
    print(f"    AUC: {blend_metrics['AUC']:.4f}, AP: {blend_metrics['AP']:.4f}, F1: {blend_metrics['F1']:.4f}")

    results_df = pd.DataFrame(results).sort_values(["AUC", "AP", "F1"], ascending=False).reset_index(drop=True)
    best_model = results_df.iloc[0]["model"]

    wide_pred = X_test.copy()
    wide_pred["y_true"] = y_test.values
    for name in MODEL_ORDER:
        wide_pred[f"prob_{name}"] = fitted[name]["proba"]
        wide_pred[f"pred_{name}"] = fitted[name]["pred"]

    return {
        "results_df": results_df,
        "best_model": best_model,
        "roc_points": roc_points,
        "pr_points": pr_points,
        "fitted": fitted,
        "importance_tables": importance_tables,
        "y_test": y_test,
        "pred_wide": wide_pred,
    }



def save_summary_excel(bundle, cfg, strict_feature_note):
    output_path = os.path.join(cfg["output_dir"], "PPP_第9部分_严格版_6模型综合对比.xlsx")
    results_df = bundle["results_df"]
    best_model = bundle["best_model"]
    pred_wide = bundle["pred_wide"]

    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        pd.DataFrame([
            ["模型数", len(results_df)],
            ["最佳模型", best_model],
            ["最高AUC", f"{results_df.iloc[0]['AUC']:.4f}"],
            ["最高AP", f"{results_df.iloc[0]['AP']:.4f}"],
            ["严格版说明", "全部6个模型统一使用3B特征集与同一train/test split"],
            ["特征说明", strict_feature_note],
        ], columns=["指标", "值"]).to_excel(writer, sheet_name="总体说明", index=False)

        results_df.to_excel(writer, sheet_name="模型比较结果", index=False)
        pred_wide.head(500).to_excel(writer, sheet_name="预测样本_前500", index=False)

        for name, table in bundle["importance_tables"].items():
            safe_sheet = ("重要性_" + name.replace("/", "_").replace("(", "").replace(")", "").replace("+", "_")[:20])[:31]
            table.to_excel(writer, sheet_name=safe_sheet, index=False)

        pd.DataFrame({
            "说明": [
                "严格版只保留一个实验口径：全部模型统一使用 categorical_features_3B。",
                "全部模型使用同一个 train/test split，避免 3A 与 3B 口径混比。",
                "PR 图中的 AP 使用 sklearn 的 average_precision_score 正式计算。",
                "DET 图使用 DetCurveDisplay.from_predictions 正式生成。",
                "Blending 的重要性为 RF/XGB/LGBM/CATB 归一化重要性的加权聚合近似。",
            ]
        }).to_excel(writer, sheet_name="口径说明", index=False)

    print(f"✓ 严格版综合对比Excel已保存: {output_path}")



def save_combined_roc_plot(roc_points_all, title, out_path):
    import matplotlib.pyplot as plt

    plt.figure(figsize=(10, 7))
    for name in MODEL_ORDER:
        df = roc_points_all[name]
        auc_val = np.trapezoid(df["tpr"], df["fpr"])
        plt.plot(
            df["fpr"], df["tpr"],
            label=f"{name} (AUC={auc_val:.3f})",
            color=MODEL_COLORS[name],
            linestyle=MODEL_LINESTYLES[name],
            linewidth=2.1,
        )
    plt.plot([0, 1], [0, 1], color="#666666", linestyle="--", linewidth=1.2, alpha=0.8, label="随机基线")
    plt.xlabel("False Positive Rate", fontsize=12)
    plt.ylabel("True Positive Rate", fontsize=12)
    plt.title(title, fontsize=14, fontweight="bold")
    plt.legend(loc="lower right", fontsize=8.5, framealpha=0.95)
    plt.grid(axis="both", alpha=0.20, linestyle="--")
    plt.tight_layout()
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"  ✓ ROC曲线图已保存: {out_path}")



def save_combined_pr_plot(bundle, title, out_path):
    import matplotlib.pyplot as plt

    plt.figure(figsize=(10, 7))
    y_test = bundle["y_test"]
    baseline = float(np.mean(y_test))

    for name in MODEL_ORDER:
        df = bundle["pr_points"][name]
        ap = average_precision_score(y_test, bundle["fitted"][name]["proba"])
        plt.plot(
            df["recall"], df["precision"],
            label=f"{name} (AP={ap:.3f})",
            color=MODEL_COLORS[name],
            linestyle=MODEL_LINESTYLES[name],
            linewidth=2.1,
        )

    plt.axhline(baseline, color="#666666", linestyle="--", linewidth=1.2, alpha=0.8, label=f"阳性基线={baseline:.3f}")
    plt.xlabel("Recall", fontsize=12)
    plt.ylabel("Precision", fontsize=12)
    plt.title(title, fontsize=14, fontweight="bold")
    plt.legend(loc="lower left", fontsize=8.5, framealpha=0.95)
    plt.grid(axis="both", alpha=0.20, linestyle="--")
    plt.tight_layout()
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"  ✓ PR曲线图已保存: {out_path}")



def save_combined_det_plot(bundle, title, out_path):
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(10, 7))
    y_test = bundle["y_test"]

    for name in MODEL_ORDER:
        display = DetCurveDisplay.from_predictions(
            y_test,
            bundle["fitted"][name]["proba"],
            name=name,
            ax=ax,
        )
        display.line_.set_color(MODEL_COLORS[name])
        display.line_.set_linestyle(MODEL_LINESTYLES[name])
        display.line_.set_linewidth(2.1)

    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.grid(axis="both", alpha=0.20, linestyle="--")
    ax.legend(loc="upper right", fontsize=8.5, framealpha=0.95)
    plt.tight_layout()
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"  ✓ DET曲线图已保存: {out_path}")



def save_threshold_curves(y_test, probas_dict, title, out_path):
    import matplotlib.pyplot as plt

    thresholds = np.linspace(0.05, 0.95, 91)
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    metric_names = ["Precision", "Recall", "F1", "Accuracy"]

    for idx, metric_name in enumerate(metric_names):
        ax = axes[idx // 2, idx % 2]
        for name in MODEL_ORDER:
            proba = probas_dict[name]
            scores = []
            for thr in thresholds:
                pred = (proba >= thr).astype(int)
                if metric_name == "Precision":
                    val = precision_score(y_test, pred, zero_division=0)
                elif metric_name == "Recall":
                    val = recall_score(y_test, pred, zero_division=0)
                elif metric_name == "F1":
                    val = f1_score(y_test, pred, zero_division=0)
                else:
                    val = accuracy_score(y_test, pred)
                scores.append(val)
            ax.plot(thresholds, scores, label=name, color=MODEL_COLORS[name], linestyle=MODEL_LINESTYLES[name], linewidth=1.8)
        ax.set_title(f"{metric_name} vs Threshold", fontsize=12, fontweight="bold")
        ax.set_xlabel("Threshold", fontsize=11)
        ax.set_ylabel(metric_name, fontsize=11)
        ax.grid(axis="both", alpha=0.20, linestyle="--")

    axes[0, 0].legend(loc="best", fontsize=8)
    plt.suptitle(title, fontsize=14, fontweight="bold", y=1.01)
    plt.tight_layout()
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"  ✓ 阈值-指标曲线图已保存: {out_path}")



def save_combined_metric_plot(results_df, title, out_path):
    import matplotlib.pyplot as plt

    metric_cols = ["AUC", "AP", "F1", "Precision", "Recall", "Accuracy"]
    models = results_df["model"].tolist()
    x = np.arange(len(models))
    width = 0.12

    plt.figure(figsize=(14, 7))
    palette = ["#1f3b73", "#2a6f97", "#6c757d", "#8c564b", "#7a5195", "#b22222"]

    for i, metric in enumerate(metric_cols):
        offset = (i - (len(metric_cols) - 1) / 2) * width
        bars = plt.bar(x + offset, results_df[metric], width, label=metric, color=palette[i], alpha=0.88)
        for bar in bars:
            h = bar.get_height()
            plt.text(bar.get_x() + bar.get_width() / 2, h, f"{h:.3f}", ha="center", va="bottom", fontsize=7)

    plt.xticks(x, models, fontsize=9, rotation=15, ha="right")
    plt.ylim(0, 1.10)
    plt.ylabel("Score", fontsize=12)
    plt.title(title, fontsize=14, fontweight="bold")
    plt.legend(loc="lower right", fontsize=9, ncol=2)
    plt.grid(axis="y", alpha=0.20, linestyle="--")
    plt.tight_layout()
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"  ✓ 合并性能对比图已保存: {out_path}")



def save_combined_importance_plot(imp_tables_all, title, out_path):
    import matplotlib.pyplot as plt

    show_models = [name for name in MODEL_ORDER if name in imp_tables_all and not imp_tables_all[name].empty]
    n_models = len(show_models)
    fig, axes = plt.subplots(1, n_models, figsize=(6.5 * n_models, 8), sharey=True)
    if n_models == 1:
        axes = [axes]

    for idx, name in enumerate(show_models):
        imp = imp_tables_all[name].head(15).iloc[::-1]
        ax = axes[idx]
        ax.barh(imp["feature"], imp["abs_importance"], color=MODEL_COLORS.get(name, "#4c4c4c"), alpha=0.90)
        ax.set_title(name, fontsize=11, fontweight="bold")
        ax.set_xlabel("Importance", fontsize=10)
        ax.grid(axis="x", alpha=0.20, linestyle="--")
    axes[0].set_ylabel("Features", fontsize=11)
    fig.suptitle(title, fontsize=14, fontweight="bold", y=1.01)
    plt.tight_layout()
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"  ✓ 合并特征重要性图已保存: {out_path}")



def save_confusion_matrices_heatmap(y_test, probas_dict, title, out_path):
    import matplotlib.pyplot as plt
    import seaborn as sns

    fig, axes = plt.subplots(2, 3, figsize=(16, 10))
    axes = axes.flatten()
    for idx, name in enumerate(MODEL_ORDER):
        pred = (probas_dict[name] >= 0.5).astype(int)
        cm = confusion_matrix(y_test, pred)
        sns.heatmap(
            cm,
            annot=True,
            fmt="d",
            cmap="Reds",
            cbar=False,
            ax=axes[idx],
            xticklabels=["Negative", "Positive"],
            yticklabels=["Negative", "Positive"],
        )
        axes[idx].set_title(name, fontsize=11, fontweight="bold")
        axes[idx].set_xlabel("Predicted", fontsize=10)
        axes[idx].set_ylabel("Actual", fontsize=10)
    plt.suptitle(title, fontsize=14, fontweight="bold", y=1.01)
    plt.tight_layout()
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"  ✓ 混淆矩阵热力图已保存: {out_path}")



def save_cost_gain_curves(y_test, probas_dict, title, out_path):
    import matplotlib.pyplot as plt

    thresholds = np.linspace(0.05, 0.95, 91)
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    tp_benefit, tn_benefit = 10, 2
    fp_cost, fn_cost = -5, -8

    for ax, curve_type in zip(axes, ["Net Benefit", "Cost-Benefit Ratio"]):
        for name in MODEL_ORDER:
            proba = probas_dict[name]
            vals = []
            for thr in thresholds:
                pred = (proba >= thr).astype(int)
                tp = ((pred == 1) & (y_test == 1)).sum()
                fp = ((pred == 1) & (y_test == 0)).sum()
                fn = ((pred == 0) & (y_test == 1)).sum()
                tn = ((pred == 0) & (y_test == 0)).sum()
                if curve_type == "Net Benefit":
                    vals.append(tp * tp_benefit + fp * fp_cost + fn * fn_cost + tn * tn_benefit)
                else:
                    benefit = tp * tp_benefit + tn * tn_benefit
                    cost = abs(fp * fp_cost + fn * fn_cost)
                    vals.append(benefit / cost if cost > 0 else 0)
            ax.plot(thresholds, vals, color=MODEL_COLORS[name], linestyle=MODEL_LINESTYLES[name], linewidth=1.8, label=name)
        ax.set_title(f"{curve_type} vs Threshold", fontsize=12, fontweight="bold")
        ax.set_xlabel("Threshold", fontsize=11)
        ax.set_ylabel(curve_type, fontsize=11)
        ax.grid(axis="both", alpha=0.20, linestyle="--")
    axes[0].legend(loc="best", fontsize=8)
    plt.suptitle(title, fontsize=14, fontweight="bold", y=1.01)
    plt.tight_layout()
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"  ✓ 成本/收益曲线图已保存: {out_path}")



def main():
    setup_chinese_fonts()
    cfg = load_config()
    ensure_output_dir(cfg["output_dir"])

    print("加载数据...")
    df = pd.read_csv(cfg["data_path"])
    print(f"数据形状: {df.shape}")

    bundle = fit_and_evaluate_strict_models(df.copy(), cfg)
    strict_feature_note = ", ".join(prepare_strict_dataset(df.copy(), cfg)["categorical_features"])
    save_summary_excel(bundle, cfg, strict_feature_note)

    results_df = bundle["results_df"]
    probas_dict = {name: bundle["fitted"][name]["proba"] for name in MODEL_ORDER}

    results_df.to_csv(
        os.path.join(cfg["output_dir"], "PPP_第9部分_严格版_6模型指标汇总.csv"),
        index=False,
        encoding="utf-8-sig",
    )
    bundle["pred_wide"].to_csv(
        os.path.join(cfg["output_dir"], "PPP_第9部分_严格版_6模型逐样本预测结果.csv"),
        index=False,
        encoding="utf-8-sig",
    )

    print("\n" + "=" * 68)
    print("生成严格版可视化图表")
    print("=" * 68)

    save_combined_roc_plot(
        bundle["roc_points"],
        "PPP项目风险识别模型 ROC 曲线对比（严格版 6 模型）",
        os.path.join(cfg["output_dir"], "PPP_第9部分_严格版_合并ROC曲线对比.png"),
    )
    save_combined_pr_plot(
        bundle,
        "PPP项目风险识别模型 PR 曲线对比（严格版 6 模型）",
        os.path.join(cfg["output_dir"], "PPP_第9部分_严格版_合并PR曲线对比.png"),
    )
    save_combined_det_plot(
        bundle,
        "PPP项目风险识别模型 DET 曲线对比（严格版 6 模型）",
        os.path.join(cfg["output_dir"], "PPP_第9部分_严格版_合并DET曲线对比.png"),
    )
    save_threshold_curves(
        bundle["y_test"],
        probas_dict,
        "PPP项目风险识别模型 阈值-指标曲线（严格版 6 模型）",
        os.path.join(cfg["output_dir"], "PPP_第9部分_严格版_阈值指标曲线.png"),
    )
    save_cost_gain_curves(
        bundle["y_test"],
        probas_dict,
        "PPP项目风险识别模型 成本/收益曲线（严格版 6 模型）",
        os.path.join(cfg["output_dir"], "PPP_第9部分_严格版_成本收益曲线.png"),
    )
    save_confusion_matrices_heatmap(
        bundle["y_test"],
        probas_dict,
        "PPP项目风险识别模型 混淆矩阵热力图（严格版 6 模型）",
        os.path.join(cfg["output_dir"], "PPP_第9部分_严格版_混淆矩阵热力图.png"),
    )
    save_combined_metric_plot(
        results_df,
        "PPP项目风险识别模型性能对比（严格版 6 模型）",
        os.path.join(cfg["output_dir"], "PPP_第9部分_严格版_合并性能对比.png"),
    )
    save_combined_importance_plot(
        bundle["importance_tables"],
        "PPP项目风险识别模型特征重要性对比（严格版 6 模型）",
        os.path.join(cfg["output_dir"], "PPP_第9部分_严格版_合并特征重要性.png"),
    )

    print("\n" + "=" * 68)
    print("严格版全部任务完成！")
    print("=" * 68)
    print(f"输出目录: {cfg['output_dir']}")
    print(f"最佳模型: {bundle['best_model']} (AUC={results_df.iloc[0]['AUC']:.4f}, AP={results_df.iloc[0]['AP']:.4f})")
    print("生成文件:")
    for f in sorted(os.listdir(cfg["output_dir"])):
        print(f"  - {f}")


if __name__ == "__main__":
    main()
