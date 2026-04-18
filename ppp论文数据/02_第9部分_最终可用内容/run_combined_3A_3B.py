
import os, pandas as pd
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from catboost import CatBoostClassifier
from plot_font_setup_cn import setup_chinese_fonts
from model_utils_no_leak import load_config, ensure_output_dir, build_no_leak_target, add_text_length_features, select_available_features, split_xy, build_preprocess, evaluate_binary_classifier, extract_feature_importance

def run_batch_a(df, cfg):
    """运行3批A模型（Logistic + Random Forest）"""
    print("="*60)
    print("开始训练模型组1（Logistic + Random Forest）")
    print("="*60)
    
    df = build_no_leak_target(df, target_col=cfg["target_col"])
    df, text_len_cols = add_text_length_features(df, cfg["text_length_cols_from"])
    num = cfg["numeric_features"] + text_len_cols
    cat = cfg["categorical_features_3A"]
    num, cat = select_available_features(df, num, cat)
    X_train, X_test, y_train, y_test = split_xy(df, num, cat, cfg["target_col"], cfg["test_size"], cfg["random_state"])
    preprocess = build_preprocess(num, cat)
    
    models = {
        "Logistic": LogisticRegression(**cfg["logistic_params"]), 
        "RandomForest": RandomForestClassifier(random_state=cfg["random_state"], **cfg["rf_params"])
    }
    
    results=[]; roc_points={}; pr_points={}; imp_tables={}; fitted={}
    for name, model in models.items():
        print(f"  训练模型: {name}")
        pipe = Pipeline([("preprocess", preprocess), ("model", model)])
        metrics, roc_df, proba, pred = evaluate_binary_classifier(pipe, X_train, X_test, y_train, y_test)
        
        # 计算PR曲线
        from sklearn.metrics import precision_recall_curve
        precision, recall, _ = precision_recall_curve(y_test, proba)
        pr_df = pd.DataFrame({"precision": precision, "recall": recall})
        
        metrics["model"] = name; results.append(metrics); roc_points[name]=roc_df; pr_points[name]=pr_df
        imp_tables[name]=extract_feature_importance(pipe,20); fitted[name]=(proba,pred)
        print(f"    AUC: {metrics['AUC']:.4f}, F1: {metrics['F1']:.4f}")
    
    results_df = pd.DataFrame(results).sort_values(["AUC","F1"], ascending=False).reset_index(drop=True)
    best = results_df.iloc[0]["model"]; best_proba, best_pred = fitted[best]
    pred_out = X_test.copy(); pred_out["y_true"]=y_test.values; pred_out["y_pred"]=best_pred; pred_out["risk_prob"]=best_proba
    
    print(f"✓ 模型组1完成！最佳模型: {best}")
    return results_df, imp_tables, best, roc_points, pr_points, fitted

def run_batch_b(df, cfg):
    """运行3批B模型（XGBoost + LightGBM + CatBoost + Blending）"""
    print("\n" + "="*60)
    print("开始训练模型组2（XGBoost + LightGBM + CatBoost + Blending）")
    print("="*60)
    
    df = build_no_leak_target(df, target_col=cfg["target_col"])
    df, text_len_cols = add_text_length_features(df, cfg["text_length_cols_from"])
    num = cfg["numeric_features"] + text_len_cols
    cat = cfg["categorical_features_3B"]
    num, cat = select_available_features(df, num, cat)
    X_train, X_test, y_train, y_test = split_xy(df, num, cat, cfg["target_col"], cfg["test_size"], cfg["random_state"])
    preprocess = build_preprocess(num, cat)
    
    # 基础模型
    base_models = {
        "XGBoost": XGBClassifier(random_state=cfg["random_state"], objective="binary:logistic", eval_metric="logloss", **cfg["xgb_params"]),
        "LightGBM": LGBMClassifier(random_state=cfg["random_state"], **cfg["lgbm_params"]),
        "CatBoost": CatBoostClassifier(random_state=cfg["random_state"], verbose=0, iterations=300, learning_rate=0.05, depth=6)
    }
    
    results=[]; roc_points={}; pr_points={}; imp_tables={}; fitted={}
    base_probas = {}  # 存储基础模型的预测概率，用于Blending
    
    for name, model in base_models.items():
        print(f"  训练模型: {name}")
        pipe = Pipeline([("preprocess", preprocess), ("model", model)])
        metrics, roc_df, proba, pred = evaluate_binary_classifier(pipe, X_train, X_test, y_train, y_test)
        
        # 计算PR曲线
        from sklearn.metrics import precision_recall_curve
        precision, recall, _ = precision_recall_curve(y_test, proba)
        pr_df = pd.DataFrame({"precision": precision, "recall": recall})
        
        metrics["model"] = name; results.append(metrics); roc_points[name]=roc_df; pr_points[name]=pr_df
        imp_tables[name]=extract_feature_importance(pipe,20); fitted[name]=(proba,pred)
        base_probas[name] = proba  # 保存预测概率
        print(f"    AUC: {metrics['AUC']:.4f}, F1: {metrics['F1']:.4f}")
    
    # 构建Blending集成模型（4个基础模型平均）
    print(f"  训练模型: Blending(RF+XGB+LGBM+CATB)")
    
    # 添加RandomForest的概率（重新训练一个RF在3B特征上）
    rf_for_blending = RandomForestClassifier(random_state=cfg["random_state"], **cfg["rf_params"])
    pipe_rf_blend = Pipeline([("preprocess", preprocess), ("model", rf_for_blending)])
    pipe_rf_blend.fit(X_train, y_train)
    rf_proba = pipe_rf_blend.predict_proba(X_test)[:, 1]
    
    # Blending：4个模型的平均
    blending_proba = np.mean([rf_proba, base_probas["XGBoost"], base_probas["LightGBM"], base_probas["CatBoost"]], axis=0)
    blending_pred = (blending_proba >= 0.5).astype(int)
    
    # 计算Blending的指标和PR曲线
    from sklearn.metrics import roc_auc_score, f1_score, precision_score, recall_score, accuracy_score, roc_curve, precision_recall_curve
    blending_auc = roc_auc_score(y_test, blending_proba)
    blending_f1 = f1_score(y_test, blending_pred)
    blending_precision = precision_score(y_test, blending_pred)
    blending_recall = recall_score(y_test, blending_pred)
    blending_accuracy = accuracy_score(y_test, blending_pred)
    blending_fpr, blending_tpr, _ = roc_curve(y_test, blending_proba)
    blending_prec, blending_rec, _ = precision_recall_curve(y_test, blending_proba)
    
    blending_metrics = {
        "AUC": blending_auc,
        "F1": blending_f1,
        "Precision": blending_precision,
        "Recall": blending_recall,
        "Accuracy": blending_accuracy,
        "train_n": len(X_train),
        "test_n": len(X_test),
        "positive_rate_test": float(y_test.mean()),
        "model": "Blending(RF+XGB+LGBM+CATB)"
    }
    results.append(blending_metrics)
    roc_points["Blending(RF+XGB+LGBM+CATB)"] = pd.DataFrame({"fpr": blending_fpr, "tpr": blending_tpr})
    pr_points["Blending(RF+XGB+LGBM+CATB)"] = pd.DataFrame({"precision": blending_prec, "recall": blending_rec})
    fitted["Blending(RF+XGB+LGBM+CATB)"] = (blending_proba, blending_pred)
    
    # Blending使用XGBoost的特征重要性作为代表
    imp_tables["Blending(RF+XGB+LGBM+CATB)"] = imp_tables["XGBoost"].copy()
    
    print(f"    AUC: {blending_auc:.4f}, F1: {blending_f1:.4f}")
    
    results_df = pd.DataFrame(results).sort_values(["AUC","F1"], ascending=False).reset_index(drop=True)
    best = results_df.iloc[0]["model"]; best_proba, best_pred = fitted[best]
    pred_out = X_test.copy(); pred_out["y_true"]=y_test.values; pred_out["y_pred"]=best_pred; pred_out["risk_prob"]=best_proba
    
    print(f"✓ 模型组2完成！最佳模型: {best}")
    return results_df, imp_tables, best, roc_points, pr_points, fitted

def generate_combined_summary(results_a, results_b, best_a, best_b, cfg):
    """生成综合对比报告"""
    print("\n" + "="*60)
    print("生成综合对比报告")
    print("="*60)
    
    # 添加批次标识
    results_a_copy = results_a.copy()
    results_b_copy = results_b.copy()
    results_a_copy["batch"] = "3A"
    results_b_copy["batch"] = "3B"
    
    # 合并所有结果
    combined_results = pd.concat([results_a_copy, results_b_copy], ignore_index=True)
    combined_results = combined_results.sort_values(["AUC","F1"], ascending=False).reset_index(drop=True)
    
    # 保存综合对比Excel
    summary_path = os.path.join(cfg["output_dir"], "PPP_第9部分_无泄漏版_全部模型综合对比.xlsx")
    with pd.ExcelWriter(summary_path, engine="openpyxl") as writer:
        # 总体说明
        pd.DataFrame([
            ["3批A最佳模型", best_a],
            ["3批B最佳模型", best_b],
            ["全局最佳模型", combined_results.iloc[0]["model"]],
            ["全局最高AUC", f"{combined_results.iloc[0]['AUC']:.4f}"]
        ], columns=["指标", "值"]).to_excel(writer, sheet_name="总体说明", index=False)
        
        # 所有模型对比
        combined_results.to_excel(writer, sheet_name="全部模型对比", index=False)
        
        # 分批次统计
        for batch_name, batch_df in [("3批A", results_a_copy), ("3批B", results_b_copy)]:
            batch_df.to_excel(writer, sheet_name=f"{batch_name}_详细结果", index=False)
        
        # 使用说明
        pd.DataFrame({
            "说明": [
                "本综合报告包含3批A和3批B的所有模型结果",
                f"3批A使用特征: {', '.join(cfg['categorical_features_3A'])}",
                f"3批B使用特征: {', '.join(cfg['categorical_features_3B'])}",
                "3批B比3批A多了'所属行业(二级行业)'特征",
                "包含CatBoost和Blending集成模型",
                "图表中已合并显示所有模型的对比结果"
            ]
        }).to_excel(writer, sheet_name="使用说明", index=False)
    
    print(f"✓ 综合对比Excel已保存: {summary_path}")
    return combined_results

def save_combined_roc_plot(roc_points_all, title, out_path):
    """保存合并的ROC曲线图（所有模型在同一张图）"""
    import matplotlib.pyplot as plt
    plt.figure(figsize=(12, 8))
    
    # 定义颜色和线型区分不同模型
    colors = {
        'Logistic': '#1f77b4', 
        'RandomForest': '#ff7f0e', 
        'XGBoost': '#2ca02c', 
        'LightGBM': '#d62728',
        'CatBoost': '#9467bd',
        'Blending(RF+XGB+LGBM+CATB)': '#8c564b'
    }
    linestyles = {
        'Logistic': '-', 
        'RandomForest': '--', 
        'XGBoost': '-.', 
        'LightGBM': ':',
        'CatBoost': (0, (3, 1, 1, 1)),
        'Blending(RF+XGB+LGBM+CATB)': (0, (5, 10))
    }
    
    for name, df in roc_points_all.items():
        color = colors.get(name, '#000000')
        linestyle = linestyles.get(name, '-')
        auc_val = np.trapezoid(df["tpr"], df["fpr"])
        plt.plot(df["fpr"], df["tpr"], 
                label=f"{name} (AUC={auc_val:.3f})", 
                color=color, linestyle=linestyle, linewidth=2.5)
    
    plt.plot([0, 1], [0, 1], 'k--', linewidth=1.5, alpha=0.5, label='随机基线')
    plt.xlabel('False Positive Rate', fontsize=13)
    plt.ylabel('True Positive Rate', fontsize=13)
    plt.title(title, fontsize=15, fontweight='bold')
    plt.legend(loc='lower right', fontsize=9, framealpha=0.9)
    plt.grid(True, alpha=0.3, linestyle='--')
    plt.tight_layout()
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  ✓ 合并ROC曲线图已保存: {out_path}")

def save_combined_pr_plot(pr_points_all, title, out_path):
    """保存合并的PR曲线图（所有模型在同一张图）"""
    import matplotlib.pyplot as plt
    plt.figure(figsize=(12, 8))
    
    # 定义颜色和线型区分不同模型
    colors = {
        'Logistic': '#1f77b4', 
        'RandomForest': '#ff7f0e', 
        'XGBoost': '#2ca02c', 
        'LightGBM': '#d62728',
        'CatBoost': '#9467bd',
        'Blending(RF+XGB+LGBM+CATB)': '#8c564b'
    }
    linestyles = {
        'Logistic': '-', 
        'RandomForest': '--', 
        'XGBoost': '-.', 
        'LightGBM': ':',
        'CatBoost': (0, (3, 1, 1, 1)),
        'Blending(RF+XGB+LGBM+CATB)': (0, (5, 10))
    }
    
    for name, df in pr_points_all.items():
        color = colors.get(name, '#000000')
        linestyle = linestyles.get(name, '-')
        # 计算Average Precision (AP)
        ap = np.trapezoid(df["precision"], df["recall"])
        plt.plot(df["recall"], df["precision"], 
                label=f"{name} (AP={ap:.3f})", 
                color=color, linestyle=linestyle, linewidth=2.5)
    
    plt.xlabel('Recall', fontsize=13)
    plt.ylabel('Precision', fontsize=13)
    plt.title(title, fontsize=15, fontweight='bold')
    plt.legend(loc='lower left', fontsize=9, framealpha=0.9)
    plt.grid(True, alpha=0.3, linestyle='--')
    plt.tight_layout()
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  ✓ 合并PR曲线图已保存: {out_path}")

def save_combined_det_plot(roc_points_all, title, out_path):
    """保存合并的DET曲线图（Detection Error Tradeoff）"""
    import matplotlib.pyplot as plt
    from scipy import stats
    
    plt.figure(figsize=(12, 8))
    
    # 定义颜色和线型
    colors = {
        'Logistic': '#1f77b4', 
        'RandomForest': '#ff7f0e', 
        'XGBoost': '#2ca02c', 
        'LightGBM': '#d62728',
        'CatBoost': '#9467bd',
        'Blending(RF+XGB+LGBM+CATB)': '#8c564b'
    }
    linestyles = {
        'Logistic': '-', 
        'RandomForest': '--', 
        'XGBoost': '-.', 
        'LightGBM': ':',
        'CatBoost': (0, (3, 1, 1, 1)),
        'Blending(RF+XGB+LGBM+CATB)': (0, (5, 10))
    }
    
    for name, df in roc_points_all.items():
        color = colors.get(name, '#000000')
        linestyle = linestyles.get(name, '-')
        
        # DET曲线使用正态逆累积分布函数转换
        fpr = df["fpr"].values
        tpr = df["tpr"].values
        
        # 避免0和1，防止inf
        fpr = np.clip(fpr, 1e-10, 1 - 1e-10)
        tpr = np.clip(tpr, 1e-10, 1 - 1e-10)
        
        # 转换为标准正态分布的z分数
        fnr = 1 - tpr  # False Negative Rate
        x_det = stats.norm.ppf(fpr)
        y_det = stats.norm.ppf(fnr)
        
        plt.plot(x_det, y_det, 
                label=name, 
                color=color, linestyle=linestyle, linewidth=2.5)
    
    plt.xlabel('False Positive Rate (norminv)', fontsize=13)
    plt.ylabel('False Negative Rate (norminv)', fontsize=13)
    plt.title(title, fontsize=15, fontweight='bold')
    plt.legend(loc='upper right', fontsize=9, framealpha=0.9)
    plt.grid(True, alpha=0.3, linestyle='--')
    plt.tight_layout()
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  ✓ 合并DET曲线图已保存: {out_path}")

def save_combined_metric_plot(results_df, title, out_path):
    """保存合并的性能指标柱状图（所有模型在同一张图）"""
    import matplotlib.pyplot as plt
    
    metric_cols = ["AUC", "F1", "Precision", "Recall", "Accuracy"]
    models = results_df["model"].tolist()
    x = np.arange(len(models))
    width = 0.15
    
    # 定义颜色
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
    
    plt.figure(figsize=(14, 7))
    for i, m in enumerate(metric_cols):
        bars = plt.bar(x + (i - 2) * width, results_df[m], width, 
                      label=m, color=colors[i], alpha=0.85, edgecolor='black', linewidth=0.5)
        # 在柱子上添加数值标签
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.3f}', ha='center', va='bottom', fontsize=7)
    
    plt.xticks(x, models, fontsize=10, rotation=15, ha='right')
    plt.ylim(0, 1.1)
    plt.ylabel('Score', fontsize=13)
    plt.xlabel('Model', fontsize=13)
    plt.title(title, fontsize=15, fontweight='bold')
    plt.legend(loc='lower right', fontsize=10)
    plt.grid(axis='y', alpha=0.3, linestyle='--')
    plt.tight_layout()
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  ✓ 合并性能对比图已保存: {out_path}")

def save_combined_importance_plot(imp_tables_all, best_model, title, out_path):
    """保存合并的特征重要性图（如果有多个模型则并排显示）"""
    import matplotlib.pyplot as plt
    
    if len(imp_tables_all) == 1:
        # 只有一个模型，直接显示
        imp = list(imp_tables_all.values())[0].head(15).iloc[::-1]
        plt.figure(figsize=(10, 8))
        plt.barh(imp["feature"], imp["abs_importance"], color='#2ca02c', alpha=0.85, edgecolor='black')
        plt.xlabel('Importance (Absolute Value)', fontsize=12)
        plt.title(f"{title}\nBest Model: {best_model}", fontsize=13, fontweight='bold')
        plt.tight_layout()
    else:
        # 多个模型，横向并排显示
        n_models = len(imp_tables_all)
        fig, axes = plt.subplots(1, n_models, figsize=(7 * n_models, 8), sharey=True)
        if n_models == 1:
            axes = [axes]
        
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
        for idx, (name, imp_df) in enumerate(imp_tables_all.items()):
            ax = axes[idx]
            imp = imp_df.head(15).iloc[::-1]
            ax.barh(imp["feature"], imp["abs_importance"], 
                   color=colors[idx % len(colors)], alpha=0.85, edgecolor='black')
            ax.set_xlabel('Importance', fontsize=10)
            ax.set_title(f'{name}', fontsize=11, fontweight='bold')
            ax.grid(axis='x', alpha=0.3, linestyle='--')
        
        axes[0].set_ylabel('Features', fontsize=12)
        fig.suptitle(title, fontsize=14, fontweight='bold', y=1.02)
        plt.tight_layout()
    
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  ✓ 合并特征重要性图已保存: {out_path}")

def save_threshold_curves(y_test, probas_dict, model_names, title, out_path):
    """保存阈值-指标曲线（Threshold Curves）"""
    import matplotlib.pyplot as plt
    from sklearn.metrics import precision_score, recall_score, f1_score
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 12))
    thresholds = np.linspace(0.1, 0.9, 50)
    
    colors = {
        'Logistic': '#1f77b4', 
        'RandomForest': '#ff7f0e', 
        'XGBoost': '#2ca02c', 
        'LightGBM': '#d62728',
        'CatBoost': '#9467bd',
        'Blending(RF+XGB+LGBM+CATB)': '#8c564b'
    }
    
    metrics_funcs = {
        'Precision': precision_score,
        'Recall': recall_score,
        'F1 Score': f1_score
    }
    
    for idx, (metric_name, metric_func) in enumerate(metrics_funcs.items()):
        ax = axes[idx // 2, idx % 2]
        for model_name, probas in zip(model_names, probas_dict):
            scores = []
            for thresh in thresholds:
                preds = (probas >= thresh).astype(int)
                if metric_name == 'Precision' and preds.sum() == 0:
                    scores.append(0)
                else:
                    scores.append(metric_func(y_test, preds, zero_division=0))
            
            color = colors.get(model_name, '#000000')
            ax.plot(thresholds, scores, label=model_name, color=color, linewidth=2)
        
        ax.set_xlabel('Threshold', fontsize=12)
        ax.set_ylabel(metric_name, fontsize=12)
        ax.set_title(f'{metric_name} vs Threshold', fontsize=13, fontweight='bold')
        ax.legend(fontsize=8, loc='best')
        ax.grid(True, alpha=0.3)
    
    # Accuracy曲线
    ax = axes[1, 1]
    from sklearn.metrics import accuracy_score
    for model_name, probas in zip(model_names, probas_dict):
        scores = []
        for thresh in thresholds:
            preds = (probas >= thresh).astype(int)
            scores.append(accuracy_score(y_test, preds))
        
        color = colors.get(model_name, '#000000')
        ax.plot(thresholds, scores, label=model_name, color=color, linewidth=2)
    
    ax.set_xlabel('Threshold', fontsize=12)
    ax.set_ylabel('Accuracy', fontsize=12)
    ax.set_title('Accuracy vs Threshold', fontsize=13, fontweight='bold')
    ax.legend(fontsize=8, loc='best')
    ax.grid(True, alpha=0.3)
    
    plt.suptitle(title, fontsize=15, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  ✓ 阈值-指标曲线图已保存: {out_path}")

def save_cost_gain_curves(y_test, probas_dict, model_names, title, out_path):
    """保存成本/收益阈值曲线"""
    import matplotlib.pyplot as plt
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    thresholds = np.linspace(0.1, 0.9, 50)
    
    colors = {
        'Logistic': '#1f77b4', 
        'RandomForest': '#ff7f0e', 
        'XGBoost': '#2ca02c', 
        'LightGBM': '#d62728',
        'CatBoost': '#9467bd',
        'Blending(RF+XGB+LGBM+CATB)': '#8c564b'
    }
    
    # 假设成本和收益参数（可根据实际业务调整）
    TP_benefit = 10  # True Positive 收益
    FP_cost = -5     # False Positive 成本
    FN_cost = -8     # False Negative 成本
    TN_benefit = 2   # True Negative 收益
    
    for ax_idx, (curve_type) in enumerate(['Net Benefit', 'Cost-Benefit Ratio']):
        ax = axes[ax_idx]
        for model_name, probas in zip(model_names, probas_dict):
            scores = []
            for thresh in thresholds:
                preds = (probas >= thresh).astype(int)
                tp = ((preds == 1) & (y_test == 1)).sum()
                fp = ((preds == 1) & (y_test == 0)).sum()
                fn = ((preds == 0) & (y_test == 1)).sum()
                tn = ((preds == 0) & (y_test == 0)).sum()
                
                if curve_type == 'Net Benefit':
                    net_benefit = (tp * TP_benefit + fp * FP_cost + 
                                  fn * FN_cost + tn * TN_benefit)
                    scores.append(net_benefit)
                else:  # Cost-Benefit Ratio
                    total_benefit = tp * TP_benefit + tn * TN_benefit
                    total_cost = abs(fp * FP_cost + fn * FN_cost)
                    ratio = total_benefit / total_cost if total_cost > 0 else 0
                    scores.append(ratio)
            
            color = colors.get(model_name, '#000000')
            ax.plot(thresholds, scores, label=model_name, color=color, linewidth=2)
        
        ax.set_xlabel('Threshold', fontsize=12)
        ax.set_ylabel(curve_type, fontsize=12)
        ax.set_title(f'{curve_type} vs Threshold', fontsize=13, fontweight='bold')
        ax.legend(fontsize=8, loc='best')
        ax.grid(True, alpha=0.3)
    
    plt.suptitle(title, fontsize=15, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  ✓ 成本/收益曲线图已保存: {out_path}")

def save_confusion_matrices_heatmap(y_test, probas_dict, model_names, title, out_path):
    """保存混淆矩阵热力图"""
    import matplotlib.pyplot as plt
    import seaborn as sns
    from sklearn.metrics import confusion_matrix
    
    n_models = len(model_names)
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    axes = axes.flatten()
    
    colors_map = plt.cm.Reds
    
    for idx, (model_name, probas) in enumerate(zip(model_names, probas_dict)):
        ax = axes[idx]
        preds = (probas >= 0.5).astype(int)
        cm = confusion_matrix(y_test, preds)
        
        sns.heatmap(cm, annot=True, fmt='d', cmap=colors_map, ax=ax,
                   xticklabels=['Negative', 'Positive'],
                   yticklabels=['Negative', 'Positive'])
        
        ax.set_xlabel('Predicted', fontsize=11)
        ax.set_ylabel('Actual', fontsize=11)
        ax.set_title(f'{model_name}', fontsize=12, fontweight='bold')
    
    # 隐藏多余的子图
    for idx in range(n_models, len(axes)):
        axes[idx].set_visible(False)
    
    plt.suptitle(title, fontsize=15, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"  ✓ 混淆矩阵热力图已保存: {out_path}")

def main():
    setup_chinese_fonts()
    cfg = load_config()
    ensure_output_dir(cfg["output_dir"])
    
    print("加载数据...")
    df = pd.read_csv(cfg["data_path"])
    print(f"数据形状: {df.shape}")
    print(f"列名: {list(df.columns)}")
    
    # 运行模型组1
    results_a, imp_a, best_a, roc_a, pr_a, fitted_a = run_batch_a(df.copy(), cfg)
    
    # 运行模型组2
    results_b, imp_b, best_b, roc_b, pr_b, fitted_b = run_batch_b(df.copy(), cfg)
    
    # 生成综合报告（Excel）
    combined = generate_combined_summary(results_a, results_b, best_a, best_b, cfg)
    
    # 保存统一的预测结果CSV
    print("\n保存统一预测结果...")
    all_predictions = []
    for batch_results, batch_name in [(results_a, "组1"), (results_b, "组2")]:
        for _, row in batch_results.iterrows():
            all_predictions.append({
                "batch": batch_name,
                "model": row["model"],
                "AUC": row["AUC"],
                "F1": row["F1"],
                "Precision": row["Precision"],
                "Recall": row["Recall"],
                "Accuracy": row["Accuracy"]
            })
    pred_df = pd.DataFrame(all_predictions)
    pred_df.to_csv(os.path.join(cfg["output_dir"], "PPP_项目风险识别_全部模型预测结果.csv"), index=False, encoding="utf-8-sig")
    
    # 准备所有模型的预测概率和真实标签（用于新图表）
    print("\n准备模型预测数据...")
    # 使用3B的特征和测试集作为基准
    df_full = build_no_leak_target(df.copy(), target_col=cfg["target_col"])
    df_full, text_len_cols = add_text_length_features(df_full, cfg["text_length_cols_from"])
    num = cfg["numeric_features"] + text_len_cols
    cat = cfg["categorical_features_3B"]
    num, cat = select_available_features(df_full, num, cat)
    X_train, X_test, y_train, y_test = split_xy(df_full, num, cat, cfg["target_col"], cfg["test_size"], cfg["random_state"])
    preprocess = build_preprocess(num, cat)
    
    # 为所有6个模型生成预测概率
    model_names = ['Logistic', 'RandomForest', 'XGBoost', 'LightGBM', 'CatBoost', 'Blending(RF+XGB+LGBM+CATB)']
    probas_list = []
    
    # 重新训练并预测所有模型（为了在同一测试集上比较）
    print("  重新训练所有模型以生成对比图表...")
    
    # 组1模型（需要在3B特征上重新训练）
    import warnings
    for name in ['Logistic', 'RandomForest']:
        if name == 'Logistic':
            model = LogisticRegression(**cfg["logistic_params"])
        else:
            model = RandomForestClassifier(random_state=cfg["random_state"], **cfg["rf_params"])
        pipe = Pipeline([("preprocess", preprocess), ("model", model)])
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", message=".*X does not have valid feature names.*")
            pipe.fit(X_train, y_train)
        proba = pipe.predict_proba(X_test)[:, 1]
        probas_list.append(proba)
    
    # 组2模型（直接使用已训练的）
    for name in ['XGBoost', 'LightGBM', 'CatBoost']:
        proba, _ = fitted_b[name]
        probas_list.append(proba)
    
    # Blending
    proba, _ = fitted_b['Blending(RF+XGB+LGBM+CATB)']
    probas_list.append(proba)
    
    # 生成合并的可视化图表（所有模型共享坐标系）
    print("\n" + "="*60)
    print("生成合并可视化图表（所有模型共享坐标系）")
    print("="*60)
    
    # 1. 合并ROC曲线图（6个模型在同一坐标系）
    roc_all = {}
    roc_all.update(roc_a)
    roc_all.update(roc_b)
    save_combined_roc_plot(
        roc_all, 
        "PPP项目风险识别模型 ROC 曲线对比（6模型）",
        os.path.join(cfg["output_dir"], "PPP_项目风险识别_合并ROC曲线对比.png")
    )
    
    # 2. 合并PR曲线图（6个模型在同一坐标系）
    pr_all = {}
    pr_all.update(pr_a)
    pr_all.update(pr_b)
    save_combined_pr_plot(
        pr_all,
        "PPP项目风险识别模型 PR 曲线对比（6模型）",
        os.path.join(cfg["output_dir"], "PPP_项目风险识别_合并PR曲线对比.png")
    )
    
    # 3. 合并DET曲线图（6个模型在同一坐标系）
    save_combined_det_plot(
        roc_all,
        "PPP项目风险识别模型 DET 曲线对比（6模型）",
        os.path.join(cfg["output_dir"], "PPP_项目风险识别_合并DET曲线对比.png")
    )
    
    # 4. 阈值-指标曲线图
    save_threshold_curves(
        y_test, probas_list, model_names,
        "PPP项目风险识别模型 阈值-指标曲线（6模型）",
        os.path.join(cfg["output_dir"], "PPP_项目风险识别_阈值指标曲线.png")
    )
    
    # 5. 成本/收益曲线图
    save_cost_gain_curves(
        y_test, probas_list, model_names,
        "PPP项目风险识别模型 成本/收益曲线（6模型）",
        os.path.join(cfg["output_dir"], "PPP_项目风险识别_成本收益曲线.png")
    )
    
    # 6. 混淆矩阵热力图
    save_confusion_matrices_heatmap(
        y_test, probas_list, model_names,
        "PPP项目风险识别模型 混淆矩阵热力图（6模型）",
        os.path.join(cfg["output_dir"], "PPP_项目风险识别_混淆矩阵热力图.png")
    )
    
    # 7. 合并性能指标柱状图（6个模型在同一张图）
    save_combined_metric_plot(
        combined,
        "PPP项目风险识别模型性能对比（6模型）",
        os.path.join(cfg["output_dir"], "PPP_项目风险识别_合并性能对比.png")
    )
    
    # 8. 合并特征重要性图（6个模型并排显示）
    imp_all = {}
    imp_all.update(imp_a)
    imp_all.update(imp_b)
    save_combined_importance_plot(
        imp_all,
        best_model=f"{best_a} (组1) / {best_b} (组2)",
        title="PPP项目风险识别模型特征重要性对比（6模型）",
        out_path=os.path.join(cfg["output_dir"], "PPP_项目风险识别_合并特征重要性.png")
    )
    
    print("\n" + "="*60)
    print("所有任务完成！")
    print("="*60)
    print(f"\n输出目录: {cfg['output_dir']}")
    print(f"\n模型组1最佳: {best_a}")
    print(f"模型组2最佳: {best_b}")
    print(f"全局最佳: {combined.iloc[0]['model']} (AUC={combined.iloc[0]['AUC']:.4f})")
    print(f"\n生成的文件:")
    for f in sorted(os.listdir(cfg["output_dir"])):
        print(f"  - {f}")

if __name__ == "__main__":
    main()
