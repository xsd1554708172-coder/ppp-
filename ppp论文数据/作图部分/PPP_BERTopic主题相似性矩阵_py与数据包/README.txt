# PPP BERTopic 主题相似性矩阵：py 文件与读取数据包

## 包内结构
- `scripts/`
  - `build_topic_similarity_matrix_revised.py`
  - `plot_topic_similarity_gnbu_official.py`
- `data/`
  - `PPP_BERTopic正式版_V2_四级十二类_实际执行版.xlsx`
  - `PPP_BERTopic文档主题分配_V2_四级十二类_实际执行版.csv`
  - `PPP_政策文本整合结果_1472篇.csv`
  - `PPP_BERTopic主题相似性矩阵_V2_四级十二类_修正版.xlsx`
- `outputs/`
  - 已放入当前已生成的图与矩阵结果，便于直接查看

## 两个脚本分别做什么
1. `build_topic_similarity_matrix_revised.py`
   - 读取 BERTopic 主题总表、文档主题分配表、1472 篇政策文本原文
   - 按主题聚合文本
   - 用字符 n-gram TF-IDF 构造主题向量
   - 计算余弦相似度并生成“修正版主题相似性矩阵”

2. `plot_topic_similarity_gnbu_official.py`
   - 读取“修正版主题相似性矩阵”
   - 按 BERTopic / Plotly 官方 `GnBu` 冰蓝色阶重绘热力图
   - 输出 PNG、SVG 和标签对照表

## 运行顺序
先运行：
`python scripts/build_topic_similarity_matrix_revised.py`

再运行：
`python scripts/plot_topic_similarity_gnbu_official.py`

## 依赖
- pandas
- numpy
- matplotlib
- scipy
- scikit-learn
- openpyxl
