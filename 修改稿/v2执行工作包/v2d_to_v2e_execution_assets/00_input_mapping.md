# v2e Input Mapping

本文件记录 `v2d → v2e` 冲刺执行包的输入来源、权威层级与禁止改动边界。

> 重要声明：本轮生成的是 `v2e` 修订执行资产与正文 patch，不是 fresh rerun 结果；任何未实际重跑的回归、图表或机制结果均标注为“未重跑，不得当作结果”。

## 1. 本轮 token 与输出目标

- 输入版本：`v2d`
- 输出目标：`v2e 顶刊冲刺执行稿 / 执行包`
- 输出目录：`修改稿/v2执行工作包/v2d_to_v2e_execution_assets/`

## 2. 本地新增核心输入

- `修改稿/v2修改建议/v2d修改建议/v2d_DID_冲刺修订报告_可下载版.docx`
  - 来源属性：本地新增文件
  - GitHub 状态：用户明确说明尚未更新到 GitHub
  - 本轮处理方式：只读解析，不覆盖、不删除、不改名
  - 抽取文本：`修改稿/v2修改建议/v2d修改建议/_codex_extracts/v2d_DID_冲刺修订报告_extracted.md`

## 3. 已读取的仓库规则与导航文件

- `AGENTS.md`
- `README_工作区导航.md`

核心约束摘要：
- `treat_share` 多期 DID / TWFE 仍是唯一主识别。
- trend-adjusted DID、leave-one-province-out、wild cluster bootstrap、log-ratio、stack/cohort 等只能作为防御性稳健性或边界诊断。
- 不得把 event study 写成已证明平行趋势。
- 不得把 `ppp_quality_zindex` 写成治理质量全面提升。
- 不得把 A/B/C/D 政策文本变量写成强机制检验。
- 不覆盖原始 `docx`、不改 `.xlsx` 原始数据、不得伪造数值。

## 4. 已读取或定位的 v2d 资产

- `修改稿/v2说明文件/v2d/00_input_mapping.md`
- `修改稿/v2说明文件/v2d/01_revision_tasklist.md`
- `修改稿/v2说明文件/v2d/02_verification_report.md`
- `修改稿/v2说明文件/v2d/03_delivery_note.md`
- `修改稿/v2说明文件/v2d/PPP论文_完整论文初稿_公共管理风格_顶刊冲刺整合稿_v2d_0419_1528.md`
- `修改稿/v2说明文件/v2d/PPP论文_完整论文初稿_公共管理风格_顶刊冲刺整合稿_v2d_0419_1528_对象保留版.docx`
- `修改稿/v2修改稿留底/v2d/v2d_0419_1528.md`
- `修改稿/v2修改稿留底/v2d/v2d_0419_1528.docx`

v2d 当前状态摘要：
- 标题、摘要、4.3、4.4、5.4、5.6 和结论已经完成谨慎收口。
- 已写入 `1472 → 1307 → 288 → 266 → 262` 样本流转。
- 已有 log-ratio 补充估计资产：`3.1916, p = 0.0277`。
- 已把 A/B/C/D 降格为政策文本证据线索。
- 明确遗留问题：城市级处理名单与原始阈值底表未显式落地。

## 5. 实证补强包

- `PPP_empirical_reinforcement_bundle_20260416_unified_v3/README.md`
- `PPP_empirical_reinforcement_bundle_20260416_unified_v3/00_unified_baseline_reference/scripts/build_unified_baseline_reference.py`
- `PPP_empirical_reinforcement_bundle_20260416_unified_v3/01_trend_adjusted_DID/scripts/run_trend_adjusted_did.py`
- `PPP_empirical_reinforcement_bundle_20260416_unified_v3/02_leave_one_province_out_jackknife/scripts/run_leave_one_province_out.py`
- `PPP_empirical_reinforcement_bundle_20260416_unified_v3/03_small_sample_inference_wild_cluster_bootstrap/scripts/summarize_small_sample_inference.py`
- `PPP_empirical_reinforcement_bundle_20260416_unified_v3/04_manuscript_integration/scripts/build_robustness_defense_summary.py`
- `PPP_empirical_reinforcement_bundle_20260416_unified_v3/04_manuscript_integration/FINAL_MANUSCRIPT_PATCH.md`
- `PPP_empirical_reinforcement_bundle_20260416_unified_v3/04_manuscript_integration/section_5_6_final.md`

本轮仅做脚本定位与轻量可解析性检查；未运行全链 rerun。

## 6. DID 文献补充目录

目录：`ppp论文数据/参考文献/did参考文献补充/`

本轮检测到 14 篇 PDF：
1. `以链养税：供应链本地化建设的财税激励逻辑_谢贞发.pdf`
2. `创新质量信号、权利稳定性与技术交易——来自专利无效宣告审查决定的经验证据_龙小宁.pdf`
3. `数字产业集群政策与关键核心技术突破式创新_师磊.pdf`
4. `数字科技企业赋能实体经济发展的效率变革——基于数字化供应链视角的理论与经验证据.pdf`
5. `数字经济发展驱动创业活跃度——基于国家大数据综合试验区的准自然实验.pdf`
6. `新城建设、土地溢价与空间错配——以国家级新区为例_曹友斌.pdf`
7. `新城新区建设与地区创业活跃度_陈勇兵.pdf`
8. `电力基础设施与企业出口规模——基于三峡工程送电的准自然实验.pdf`
9. `破产司法改革与稳就业：来自企业破产审理方式改革试点的证据.pdf`
10. `社保征管体制改革、人口迁移与非正规就业.pdf`
11. `算力部署、数据跨域流动与企业全要素生产率——来自智算中心的证据_许诺.pdf`
12. `统一市场准入与企业创新行为：结构估计与机制分解_侯建翔.pdf`
13. `行政区划改革如何差异化影响土地资源配置_张星铜.pdf`
14. `行政诉讼跨区划管辖与企业社保遵从_潘越.pdf`

文献使用边界：
- 本轮优先依据 `v2d_DID_冲刺修订报告` 对这些文献的摘要性整理。
- 未逐篇全文抽取 PDF 元数据与页码。
- 不编造卷期页码、控制变量、固定效应或显著性。

## 7. 本轮不会修改的高风险文件

- `修改稿/v2修改建议/v2d修改建议/v2d_DID_冲刺修订报告_可下载版.docx`
- `修改稿/v2说明文件/v2d/*.docx`
- `修改稿/v2修改稿留底/v2d/*.docx`
- `数据总表（一切数据基础）.xlsx`
- `ppp论文数据/*.xlsx`
- `.env`、密钥、生产配置

## 8. authority hierarchy

1. `AGENTS.md`
2. `README_工作区导航.md`
3. 本地 `v2d_DID_冲刺修订报告_可下载版.docx`
4. v2d 已落地 verification / delivery / manuscript-facing 资产
5. 官方结果表与变量口径表
6. empirical reinforcement bundle 的 README、脚本与已落地输出
7. DID 补充文献目录与本地 PDF 文件名
8. 未能从当前文件核实的旧日志或远程信息

---

## 2026-04-20 人工确认补充输入

用户已补充确认以下事实并授权执行：

- 当前无 city-year treatment registry 原始城市名单。
- 当前无处理阈值底表。
- `treat_share` 聚合权重未知；本轮允许按情况合理判断，因此采用等权城市计数作为审计默认基准。
- 允许生成派生 CSV/XLSX 模板。
- rerun 环境未知；若对文章有利且必要，由 Codex 执行必要环境补齐。本轮因此安装 `matplotlib`、`statsmodels`、`patsy`。
- 需要逐篇解析 14 篇 DID PDF 并输出对应元数据。
- 允许进入 full rerun 阶段。

该补充输入不改变主识别：`treat_share` 多期 DID / TWFE 仍是唯一主识别。
