
import json, os
from typing import Dict, List, Tuple
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score, roc_curve
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
import matplotlib.pyplot as plt

def load_config(config_path="config.json")->Dict:
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)

def ensure_output_dir(output_dir:str)->None:
    os.makedirs(output_dir, exist_ok=True)

def build_no_leak_target(df: pd.DataFrame, target_col="risk_struct_clean")->pd.DataFrame:
    out = df.copy()
    high_risk = (
        (out.get("is_prep", 0) == 1) |
        (out.get("is_proc", 0) == 1) |
        (out.get("fiscal_pass", 0) == 0) |
        (out.get("vfm_pass", 0) == 0)
    )
    low_risk = (
        (out.get("is_exec", 0) == 1) &
        (out.get("fiscal_pass", 0) == 1) &
        (out.get("vfm_pass", 0) == 1)
    )
    out[target_col] = np.where(high_risk, 1, np.where(low_risk, 0, np.nan))
    out = out.dropna(subset=[target_col]).copy()
    out[target_col] = out[target_col].astype(int)
    return out

def add_text_length_features(df: pd.DataFrame, source_cols: List[str])->Tuple[pd.DataFrame, List[str]]:
    out = df.copy()
    created = []
    for c in source_cols:
        if c in out.columns:
            new_c = f"{c}_len"
            out[new_c] = out[c].fillna("").astype(str).str.len()
            created.append(new_c)
    return out, created

def select_available_features(df: pd.DataFrame, numeric_features: List[str], categorical_features: List[str])->Tuple[List[str], List[str]]:
    return [c for c in numeric_features if c in df.columns], [c for c in categorical_features if c in df.columns]

def split_xy(df: pd.DataFrame, numeric_features: List[str], categorical_features: List[str], target_col: str, test_size: float, random_state:int):
    X = df[numeric_features + categorical_features].copy()
    y = df[target_col].copy()
    return train_test_split(X, y, test_size=test_size, random_state=random_state, stratify=y)

def build_preprocess(numeric_features: List[str], categorical_features: List[str])->ColumnTransformer:
    numeric_transformer = Pipeline([("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler())])
    categorical_transformer = Pipeline([("imputer", SimpleImputer(strategy="most_frequent")), ("onehot", OneHotEncoder(handle_unknown="ignore"))])
    return ColumnTransformer([("num", numeric_transformer, numeric_features), ("cat", categorical_transformer, categorical_features)])

def evaluate_binary_classifier(pipe, X_train, X_test, y_train, y_test):
    import warnings
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message=".*X does not have valid feature names.*")
        pipe.fit(X_train, y_train)
        proba = pipe.predict_proba(X_test)[:,1]
        pred = (proba >= 0.5).astype(int)
    fpr, tpr, _ = roc_curve(y_test, proba)
    metrics = {
        "AUC": roc_auc_score(y_test, proba),
        "F1": f1_score(y_test, pred),
        "Precision": precision_score(y_test, pred),
        "Recall": recall_score(y_test, pred),
        "Accuracy": accuracy_score(y_test, pred),
        "train_n": len(X_train),
        "test_n": len(X_test),
        "positive_rate_test": float(y_test.mean()),
    }
    return metrics, pd.DataFrame({"fpr":fpr,"tpr":tpr}), proba, pred

def extract_feature_importance(pipe, topn=20):
    feat_names = pipe.named_steps["preprocess"].get_feature_names_out()
    model = pipe.named_steps["model"]
    if hasattr(model, "coef_"):
        imp = pd.DataFrame({"feature": feat_names, "importance": model.coef_[0]})
    else:
        imp = pd.DataFrame({"feature": feat_names, "importance": model.feature_importances_})
    imp["abs_importance"] = imp["importance"].abs()
    return imp.sort_values("abs_importance", ascending=False).head(topn)

def save_roc_plot(roc_points, title, out_path):
    plt.figure(figsize=(7,5))
    for name, df in roc_points.items():
        plt.plot(df["fpr"], df["tpr"], label=name)
    plt.plot([0,1],[0,1], linestyle="--")
    plt.xlabel("False Positive Rate"); plt.ylabel("True Positive Rate"); plt.title(title); plt.legend(); plt.tight_layout()
    plt.savefig(out_path, dpi=220); plt.close()

def save_metric_plot(results_df, title, out_path):
    metric_cols = ["AUC","F1","Precision","Recall","Accuracy"]
    x = np.arange(len(results_df)); width = 0.15
    plt.figure(figsize=(8,5))
    for i, m in enumerate(metric_cols):
        plt.bar(x + (i-2)*width, results_df[m], width, label=m)
    plt.xticks(x, results_df["model"]); plt.ylim(0,1.05); plt.ylabel("Score"); plt.title(title); plt.legend(); plt.tight_layout()
    plt.savefig(out_path, dpi=220); plt.close()

def save_importance_plot(importance_df, title, out_path):
    imp = importance_df.head(15).iloc[::-1]
    plt.figure(figsize=(8,6))
    plt.barh(imp["feature"], imp["abs_importance"])
    plt.xlabel("Importance"); plt.title(title); plt.tight_layout()
    plt.savefig(out_path, dpi=220); plt.close()
