# 第9部分方案A：无标签泄漏版项目级风险识别代码包

本代码包是第9部分最终建议采用的版本。

## 标签定义（无泄漏版）
- `risk_struct_clean = 1`：满足任一
  - is_prep == 1
  - is_proc == 1
  - fiscal_pass == 0
  - vfm_pass == 0
- `risk_struct_clean = 0`：同时满足
  - is_exec == 1
  - fiscal_pass == 1
  - vfm_pass == 1

也就是说：
- 标签只由结构/制度结果定义
- risk_text_count 不再参与标签定义
- 文本变量只作为预测特征

## 主文件
- run_3A_logistic_rf_no_leak.py
- run_3B_xgb_lgbm_no_leak.py

## 输入文件
请把 `PPP_project_level_risk_model_data_v2_无泄漏严格版.csv` 放在同目录，或在 config.json 中修改 data_path。

## 运行
pip install -r requirements.txt
python run_3A_logistic_rf_no_leak.py
python run_3B_xgb_lgbm_no_leak.py

## 任务边界
- 本任务更适合被解释为项目级高/低风险排序与识别，而不是对全部 PPP 项目进行全口径风险评级。
- 当前 AUC 约 0.85 表示中等偏强的可预测性，不应被表述为模型可以替代制度治理。
- 提升类模型之间性能接近属于正常现象；Blending 仅略优，不宜夸写为压倒性最优。


## 2026-04-12 v3补充：预测任务边界
- 第9部分是基于结构性高/低风险定义的排序/识别任务。
- 严禁写成“模型可替代制度治理”或“模型直接给出政策裁决”。
- 建议正文保留6模型透明对比表，并将Blending/XGBoost等提升类模型写成“总体接近、Blending略优”。
