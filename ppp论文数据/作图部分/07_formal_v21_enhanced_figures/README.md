# Formal V21 Enhanced Figure Bundle

This folder contains a new, non-conflicting figure bundle built on the current formal package boundary.

## What this bundle does

- Uses only the currently adopted official entities for the main evidence chain.
- Avoids reintroducing deprecated PCA-centered main-result writing.
- Compresses part 9 into one dense candidate figure rather than a large block of ML-only figures.
- Adds high-information-density figures that can support the paper without overriding the current table-first writing plan.

## Files

- `code/generate_formal_v21_enhanced_figures.py`: generation script
- `charts/`: generated `.png/.pdf/.svg` outputs plus `contact_sheet.png`
- `metadata/source_manifest.csv`: figure-level source and boundary log

## Figure list

- `Figure_0_official_evidence_architecture`
  - Purpose: make the paper's data-layer workload visible in one overview figure.
  - Best use: introduction or data section.
- `Figure_4X_text_construction_dashboard`
  - Purpose: show corpus throughput, province-year coverage, A/B/C/D evolution, and top-topic heat strips.
  - Best use: Part 3-4 main text.
- `Figure_5X_baseline_effect_matrix`
  - Purpose: compactly show all three official 5.3 treatment definitions against the three core outcomes.
  - Best use: Part 5 main text.
- `Figure_5Y_event_study_dashboard`
  - Purpose: show dynamic coefficients while making the lead-term caveat explicit.
  - Best use: Part 5 main text or appendix.
- `Figure_6X_mechanism_evidence_matrix`
  - Purpose: summarize direct effects, mediator paths, chain continuity, and strict-mediation failure in one dense figure.
  - Best use: Part 6 main text.
- `Figure_8X_robustness_compass`
  - Purpose: compress the robustness section into one aligned scorecard and a separate IV-feasibility strip.
  - Best use: Part 8 main text.
- `Figure_9X_model_frontier_consensus`
  - Purpose: replace multiple part-9 performance plots with one frontier-plus-consensus figure.
  - Best use: appendix first; selective main-text use only.

## Official local evidence basis

The script pulls from the current adopted entities only:

- text-construction layer:
  - `PPP_doc_level_variables_v3_DID主识别窗口_2014_2022_地方样本_实际执行版_20260413_0912.csv`
  - `PPP_province_year_variables_v3_DID主识别窗口_方案2_平衡口径_实际执行版_20260413_0912.csv`
- DID / event-study / mechanism / robustness layer:
  - `PPP_3.6_model_ready_panel_v3_统一口径_方案2_实际执行版_20260413_1048.csv`
  - `PPP_第5部分_5.3正式回归结果长表_V3_重估版_20260413_1048.csv`
  - `PPP_第5部分_5.4动态系数长表_V3_重估版_20260413_1048.csv`
  - `PPP_第6部分_6.1-6.4结果方程含中介_V2_四级十二类_实际执行版.csv`
  - `PPP_第6部分_6.5链式机制路径长表_V2_四级十二类_实际执行版.csv`
  - `PPP_第6部分_6.6严格中介效应分解结果长表_V2_四级十二类_实际执行版.csv`
  - `PPP_第8部分_8.1-8.3常规稳健性结果长表_V3_重估版_20260413_1048.csv`
  - `PPP_第8部分_8.4PSM-DID结果长表_V3_重估版_20260413_1048.csv`
  - `PPP_第8部分_8.5候选IV筛查长表_V3_重估版_20260413_1048.csv`
  - `PPP_第8部分_8.6DML结果汇总_V3_重估版_20260413_1048.csv`
- part 9:
  - `PPP_project_level_risk_model_data_v3_无泄漏严格版_标签统一_20260413_1048.csv`
  - `PPP_第9部分_严格版_6模型综合对比.xlsx`
  - `PPP_第9部分_严格版_6模型逐样本预测结果.csv`

## External design and metric references

The visual design and metric choices were aligned to a small set of authoritative references:

- Bang Wong, *Nature Methods*:
  - ["Points of view: Gestalt principles (Part 1)"](https://www.nature.com/articles/nmeth.1618)
  - ["Points of view: Arrows"](https://www.nature.com/articles/nmeth.1938)
  - ["Points of view: The overview figure"](https://www.nature.com/articles/nmeth.1720)
  - ["Points of view: Legends"](https://www.nature.com/articles/nmeth.1758)
  - ["Points of significance: Bar charts and box plots"](https://www.nature.com/articles/nmeth.2659)
- Rougier, Droettboom, Bourne, *PLOS Computational Biology*:
  - ["Ten Simple Rules for Better Figures"](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1003833)
- Saito and Rehmsmeier, *PLOS ONE*:
  - ["The Precision-Recall Plot Is More Informative than the ROC Plot When Evaluating Binary Classifiers on Imbalanced Datasets"](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0118432)
- scikit-learn official documentation:
  - ["Precision-Recall example"](https://scikit-learn.org/stable/auto_examples/model_selection/plot_precision_recall.html)
  - ["precision_recall_curve API"](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.precision_recall_curve.html)

## Internal literature inspiration from your reference pack

- `A3 PPP政策内容分析及其市场影响`: PPP-domain topic intensity and evolution
- `A4 经济增长目标引领与项目推进`: PPP progress structure and project interpretation
- `B4 大数据综合试验区提升企业数据资产化的机制`: DID + mechanism + robustness organization
- `B5 数字风险治理`: part-9 risk task framing
- `C1 基于BERTopic的...主题及演化分析`: topic-evolution heat strips
- `C2 政策信息学视角下政策文本量化方法研究进展`: text-quantification architecture
- `C3 注册制改革、信息披露与投资者行为`: information-density DID writing and figure-table coordination

## Boundary reminders

- Part 5 figures are built around `exec_share`, `proc_share`, and `ppp_quality_zindex` only.
- Event-study graphics are explicitly labeled as dynamic displays, not strong pre-trend proof.
- Mechanism graphics are written to support "partial evidence" rather than "complete stable chain."
- Part 9 is compressed on purpose: one dense candidate figure instead of a figure-heavy ML section.
