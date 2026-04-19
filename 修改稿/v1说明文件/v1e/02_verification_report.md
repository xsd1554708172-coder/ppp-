# 02_verification_report

- token: `v1e`
- verification_time: `2026-04-19 Asia/Shanghai`

## 1. 核验对象

1. `C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\修改稿\v1说明文件\v1e\PPP论文_完整论文初稿_公共管理风格_顶刊冲刺整合稿_v1e_0419_2307.md`
2. `C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\修改稿\v1说明文件\v1e\PPP论文_完整论文初稿_公共管理风格_顶刊冲刺整合稿_v1e_0419_2307.docx`
3. `C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\修改稿\v1说明文件\v1e\fresh_rerun_main_results_20260419.csv`
4. `C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\修改稿\v1说明文件\v1e\fresh_rerun_vs_official_20260419.csv`
5. `C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\修改稿\v1说明文件\v1e\appendix_B_log_ratio_reestimate_20260419.csv`
6. `C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\修改稿\v1说明文件\v1e\appendix_C_sample_flow_20260419.csv`
7. `C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\修改稿\v1说明文件\v1e\docx_generation_log_0419_2307.md`

## 2. 主识别与论文红线核查

### 2.1 主识别是否仍为唯一主模型

- 结果：**通过**
- 证据：`v1e` 正文在摘要、4.4、5.2、结论中都将主识别明确写为 `treat_share` 多期 DID / TWFE。
- 未发现把 trend-adjusted DID、stack DID、cohort ATT、PSM-DID、DML、IV candidate 或机器学习抬升为主识别/第二主模型的写法。

### 2.2 是否误写 event study

- 结果：**通过**
- 证据：正文明确把 event study 限定为动态路径和识别边界说明，没有写成“证明平行趋势成立”。

### 2.3 是否误抬高 `ppp_quality_zindex`

- 结果：**通过**
- 证据：摘要、5.2、5.6、结论都明确写出该指标方向上可讨论，但统计上不够稳定，不能承担全文主结论。

### 2.4 是否把机器学习写成因果识别

- 结果：**通过**
- 证据：正文将项目级模型限定为治理辅助识别/排序工具，不参与主识别抬升。

## 3. fresh rerun / reconstruction 结果核查

### 3.1 5.3 基准 DID/TWFE fresh rerun

- 结果：**通过**
- 数据来源：`fresh_rerun_vs_official_20260419.csv`
- fresh rerun 与官方 5.3 长表在机器精度上对齐：
  - `exec_share`: fresh `0.355627705482334` vs official `0.3556277047526408`，gap `7.30e-10`
  - `proc_share`: fresh `-0.40227748799594565` vs official `-0.4022774860927093`，gap `-1.90e-09`
  - `ppp_quality_zindex`: fresh `0.5252969367347973` vs official `0.5252969355953995`，gap `1.14e-09`
- manuscript-facing 写法已同步为四位小数：`0.3556 / -0.4023 / 0.5253`。

### 3.2 对数比率补充估计

- 结果：**通过**
- 数据来源：`appendix_B_log_ratio_reestimate_20260419.csv`
- 基准 continuity rule = `half_min_positive` 时：
  - `coef = 3.191616610013625`
  - `se = 1.449999183787818`
  - `p = 0.027727802789347278`
- 正文与摘要已同步写为：`3.1916, p = 0.0277`。

### 3.3 样本流转链条

- 结果：**通过**
- 数据来源：`appendix_C_sample_flow_20260419.csv`
- 已统一为：
  - `1472` 全文池
  - `1307` DID 主识别窗口文本文档
  - `288` province-year 平衡窗口
  - `266` 正式 V3 主面板观测
  - `262` 5.3 正式估计样本
- 正文 4.1、附录 C 与说明文件三处已同步。

### 3.4 删样说明

- 结果：**通过**
- 数据来源：`appendix_A_sample_exclusions_20260419.csv`
- 4 个被排除观测均为新疆生产建设兵团，年份为 `2015 / 2016 / 2017 / 2020`，原因均为 8 个基准控制变量缺失。

## 4. manuscript-facing 防守值核查

### 4.1 trend-adjusted DID

- 结果：**通过，但保留边界说明**
- 正文保留的 manuscript-facing 防守值为：
  - `exec_share = 0.2263, p = 0.1945`
  - `proc_share = -0.3521, p = 0.0485`
  - `ppp_quality_zindex = -0.1699, p = 0.6780`
- 说明：本轮零依赖手工 fresh rerun 得到的 trend-adjusted 值为：
  - `exec_share ≈ 0.2391, p ≈ 0.1727`
  - `proc_share ≈ -0.3605, p ≈ 0.0396`
  - `ppp_quality_zindex ≈ -0.1115, p ≈ 0.7946`
- 处理：由于手工 fresh rerun 与已落地官方 bundle 值不完全一致，**正文未用 fresh 手工值覆盖官方 manuscript-facing 数字**，而是将 fresh 手工值仅保留为 diagnostic artifact。

### 4.2 wild cluster bootstrap

- 结果：**正文值已同步；fresh rerun 未执行**
- 正文 / 附录 D 统一保留官方已落地数值：
  - `exec_share p = 0.0761`
  - `proc_share p = 0.1221`
  - `ppp_quality_zindex p = 0.2372`
- blocker：当前环境缺少可直接一键运行的完整运行链与依赖环境，因此本轮未伪造 fresh rerun。

## 5. 文稿与附件同步核查

- 摘要、4.1、4.3、4.4、5.2、5.4、5.6、结论：**已同步**
- 附录 A-E：**已插入 md 与 docx**
- 透明度说明：**已补入 rerun 与 blocker 说明**
- “政策文本证据线索”降格写法：**已同步**
- “条件关联证据”副题：**已同步**

## 6. `.docx` 对象保留核查

- 生成方式：复制源 `v1d` docx 全包，仅替换 `word/document.xml`
- fresh 核验结果：
  - source entry count = `23`
  - output entry count = `23`
  - source media count = `12`
  - output media count = `12`
  - charts = `0 -> 0`
  - embeddings = `0 -> 0`
- 结论：**对象包结构保持一致，通过对象保留检查**。

## 7. 数据修改核查

- 原始 `.xlsx` 工作簿：**未修改**
- 原始 `source of truth` 文件：**未覆盖**
- 本轮仅新增脚本、派生结果、说明文件与修订稿。

## 8. 结论

本轮 `v1e` 在以下意义上通过 fresh verification：

1. 唯一主识别仍为 `treat_share` DID / TWFE；
2. 基准 DID fresh rerun 已与官方 5.3 长表在机器精度上对齐；
3. log-ratio 补充估计已 fresh rerun 并同步到正文；
4. `ppp_quality_zindex`、event study、机器学习三条红线均未越界；
5. `.docx` 已生成且对象包结构保持一致；
6. 未执行的 wild cluster fresh rerun 与未完全闭合的 trend-adjusted 手工 rerun 已被显式标记为边界/ blocker，而非被伪装成“已完成”。
