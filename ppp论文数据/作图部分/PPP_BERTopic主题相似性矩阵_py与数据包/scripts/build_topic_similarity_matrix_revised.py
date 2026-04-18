# -*- coding: utf-8 -*-
"""
基于文档级原文本重建 BERTopic 主题相似性矩阵（修正版）
输入：
1) data/PPP_BERTopic正式版_V2_四级十二类_实际执行版.xlsx
2) data/PPP_BERTopic文档主题分配_V2_四级十二类_实际执行版.csv
3) data/PPP_政策文本整合结果_1472篇.csv
输出：
- outputs/PPP_BERTopic主题相似性矩阵_V2_四级十二类_修正版.xlsx
- outputs/PPP_BERTopic主题相似性矩阵_V2_四级十二类_修正版.png
- outputs/PPP_BERTopic主题相似性矩阵_V2_四级十二类_修正版_说明.md
"""
import os
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from scipy.cluster.hierarchy import linkage, leaves_list

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
OUT = os.path.join(ROOT, "outputs")
os.makedirs(OUT, exist_ok=True)

topic_xlsx = os.path.join(DATA, "PPP_BERTopic正式版_V2_四级十二类_实际执行版.xlsx")
assign_csv = os.path.join(DATA, "PPP_BERTopic文档主题分配_V2_四级十二类_实际执行版.csv")
text_csv = os.path.join(DATA, "PPP_政策文本整合结果_1472篇.csv")

topic_df = pd.read_excel(topic_xlsx, sheet_name="主题总表").copy()
assign_df = pd.read_csv(assign_csv)
text_df = pd.read_csv(text_csv)

merged = assign_df.merge(text_df[["序号", "文件内容"]], on="序号", how="left")

def clean_text(s: str) -> str:
    s = "" if pd.isna(s) else str(s)
    s = re.sub(r"http[s]?://\S+", " ", s)
    s = re.sub(r"FBM-CLI\.[\d\.]+", " ", s)
    s = re.sub(r"\s+", " ", s)
    return s.strip()

merged["文件内容"] = merged["文件内容"].apply(clean_text)

topic_corpus = (
    merged.groupby("topic")["文件内容"]
    .apply(lambda x: " ".join([t for t in x if t]))
    .reset_index()
    .rename(columns={"topic": "主题编号", "文件内容": "聚合文本"})
)

topic_corpus = topic_df[["主题编号", "主题名称", "映射一级主题名称", "映射二级主题", "文档数"]].merge(
    topic_corpus, on="主题编号", how="left"
)
topic_corpus["聚合文本"] = topic_corpus["聚合文本"].fillna("")

# 对中文更稳：用字符 n-gram 构造主题向量
vectorizer = TfidfVectorizer(analyzer="char", ngram_range=(2, 4), min_df=1, max_features=8000)
X = vectorizer.fit_transform(topic_corpus["聚合文本"])
sim = cosine_similarity(X)

# 聚类重排
link = linkage(X.toarray(), method="average", metric="cosine")
order = leaves_list(link)
topic_corpus_ord = topic_corpus.iloc[order].reset_index(drop=True)
sim_ord = sim[np.ix_(order, order)]
labels = [f"T{int(t)}" for t in topic_corpus_ord["主题编号"].tolist()]
sim_df = pd.DataFrame(sim_ord, index=labels, columns=labels)

pairs = []
orig_idx = topic_corpus.reset_index(drop=True)
for i in range(len(orig_idx)):
    for j in range(i + 1, len(orig_idx)):
        pairs.append({
            "topic_i": int(orig_idx.loc[i, "主题编号"]),
            "topic_i_name": orig_idx.loc[i, "主题名称"],
            "topic_i_primary": orig_idx.loc[i, "映射一级主题名称"],
            "topic_i_secondary": orig_idx.loc[i, "映射二级主题"],
            "topic_j": int(orig_idx.loc[j, "主题编号"]),
            "topic_j_name": orig_idx.loc[j, "主题名称"],
            "topic_j_primary": orig_idx.loc[j, "映射一级主题名称"],
            "topic_j_secondary": orig_idx.loc[j, "映射二级主题"],
            "cosine_similarity": float(sim[i, j])
        })
pairs_df = pd.DataFrame(pairs).sort_values("cosine_similarity", ascending=False).reset_index(drop=True)

out_xlsx = os.path.join(OUT, "PPP_BERTopic主题相似性矩阵_V2_四级十二类_修正版.xlsx")
with pd.ExcelWriter(out_xlsx, engine="openpyxl") as writer:
    sim_df.to_excel(writer, sheet_name="相似性矩阵")
    pairs_df.to_excel(writer, sheet_name="最相近主题对", index=False)
    topic_corpus_ord[["主题编号", "主题名称", "映射一级主题名称", "映射二级主题", "文档数"]].assign(
        heatmap_label=labels
    ).to_excel(writer, sheet_name="热力图标签对照", index=False)
    topic_corpus[["主题编号", "主题名称", "映射一级主题名称", "映射二级主题", "文档数"]].to_excel(
        writer, sheet_name="主题元信息", index=False
    )

fig, ax = plt.subplots(figsize=(12, 10))
im = ax.imshow(sim_ord, aspect="auto")
ax.set_xticks(range(len(labels)))
ax.set_yticks(range(len(labels)))
ax.set_xticklabels(labels, rotation=90, fontsize=8)
ax.set_yticklabels(labels, fontsize=8)
ax.set_title("BERTopic Topic Similarity Matrix (Cosine on Aggregated Topic Texts)")
cbar = plt.colorbar(im, ax=ax)
cbar.set_label("Cosine similarity")
plt.tight_layout()

out_png = os.path.join(OUT, "PPP_BERTopic主题相似性矩阵_V2_四级十二类_修正版.png")
plt.savefig(out_png, dpi=240, bbox_inches="tight")
plt.close(fig)

out_md = os.path.join(OUT, "PPP_BERTopic主题相似性矩阵_V2_四级十二类_修正版_说明.md")
with open(out_md, "w", encoding="utf-8") as f:
    f.write("# PPP BERTopic 主题相似性矩阵（修正版）\n\n")
    f.write("## 口径\n")
    f.write("- 基于 BERTopic 导出结果与文档级原文本。\n")
    f.write("- 回到文档级原文本，将同一主题下的文档文本聚合为主题文本。\n")
    f.write("- 用字符 n-gram TF-IDF 构造主题向量，以余弦相似度生成主题相似性矩阵。\n")
    f.write("- 最后用层次聚类重排矩阵顺序，增强可读性。\n")
print("完成：", out_xlsx)
