
import os, pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from plot_font_setup_cn import setup_chinese_fonts
from model_utils_no_leak import load_config, ensure_output_dir, build_no_leak_target, add_text_length_features, select_available_features, split_xy, build_preprocess, evaluate_binary_classifier, extract_feature_importance, save_roc_plot, save_metric_plot, save_importance_plot

def main():
    setup_chinese_fonts()
    cfg = load_config()
    ensure_output_dir(cfg["output_dir"])
    df = pd.read_csv(cfg["data_path"])
    df = build_no_leak_target(df, target_col=cfg["target_col"])
    df, text_len_cols = add_text_length_features(df, cfg["text_length_cols_from"])
    num = cfg["numeric_features"] + text_len_cols
    cat = cfg["categorical_features_3A"]
    num, cat = select_available_features(df, num, cat)
    X_train, X_test, y_train, y_test = split_xy(df, num, cat, cfg["target_col"], cfg["test_size"], cfg["random_state"])
    preprocess = build_preprocess(num, cat)
    models = {"Logistic": LogisticRegression(**cfg["logistic_params"]), "RandomForest": RandomForestClassifier(random_state=cfg["random_state"], **cfg["rf_params"])}
    results=[]; roc_points={}; imp_tables={}; fitted={}
    for name, model in models.items():
        pipe = Pipeline([("preprocess", preprocess), ("model", model)])
        metrics, roc_df, proba, pred = evaluate_binary_classifier(pipe, X_train, X_test, y_train, y_test)
        metrics["model"] = name; results.append(metrics); roc_points[name]=roc_df; imp_tables[name]=extract_feature_importance(pipe,20); fitted[name]=(proba,pred)
    results_df = pd.DataFrame(results).sort_values(["AUC","F1"], ascending=False).reset_index(drop=True)
    best = results_df.iloc[0]["model"]; best_proba, best_pred = fitted[best]
    pred_out = X_test.copy(); pred_out["y_true"]=y_test.values; pred_out["y_pred"]=best_pred; pred_out["risk_prob"]=best_proba
    xlsx = os.path.join(cfg["output_dir"], "PPP_第9部分第3批A_无泄漏版_项目级风险识别模型比较.xlsx")
    with pd.ExcelWriter(xlsx, engine="openpyxl") as writer:
        pd.DataFrame([["最佳模型",best]], columns=["item","value"]).to_excel(writer, sheet_name="分析说明", index=False)
        results_df.to_excel(writer, sheet_name="模型比较结果", index=False)
        pred_out.head(500).to_excel(writer, sheet_name="最佳模型预测样本_前500", index=False)
        for n,t in imp_tables.items(): t.to_excel(writer, sheet_name=f"重要性_{n[:20]}", index=False)
    pred_out.to_csv(os.path.join(cfg["output_dir"], "PPP_project_risk_best_model_predictions_3A_no_leak.csv"), index=False, encoding="utf-8-sig")
    save_roc_plot(roc_points, "项目级风险识别模型 ROC 曲线比较（3批A，无泄漏版）", os.path.join(cfg["output_dir"], "PPP_第9部分第3批A_无泄漏版_ROC曲线比较.png"))
    save_metric_plot(results_df, "项目级风险识别模型性能比较（3批A，无泄漏版）", os.path.join(cfg["output_dir"], "PPP_第9部分第3批A_无泄漏版_模型性能比较.png"))
    save_importance_plot(imp_tables[best], f"最佳模型特征重要性（3批A，无泄漏版）：{best}", os.path.join(cfg["output_dir"], "PPP_第9部分第3批A_无泄漏版_最佳模型特征重要性.png"))
if __name__ == "__main__":
    main()
