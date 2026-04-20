# v2e DID 冲刺修订执行计划

> 本计划是 `v2d → v2e` 的执行蓝图，不是实证结果文件。未实际运行的内容均标注为“未重跑，不得当作结果”。

## 总目标

以 `v2d` 为底座推进 `v2e`，但不继续停留在语言润色层面，而是补齐审稿人可逐段追查的硬证据链：

1. city-year treatment registry；
2. province-year `treat_share` 聚合审计；
3. 全链 fresh rerun；
4. 防御性稳健性分层整理；
5. 独立机制变量；
6. 文本变量效度审计；
7. 14 篇 DID 文献嵌入；
8. 主识别、防守检验、边界诊断、扩展分析分层写法。

## 执行单元 A：city-year treatment registry

### 输入文件

- 待补：城市级改革/处理名单原始表
- 待补：处理阈值底表
- 参考：`修改稿/v2说明文件/v2d/appendix_A_treat_share_definition_tables_20260418.md`
- 参考：`修改稿/v2说明文件/v2d/appendix_A_treat_share_reconstruction_20260418.csv`

### 输出文件

- `appendix_A0_city_year_treatment_registry.csv`
- `appendix_A0_city_year_treatment_registry_codebook.md`

### 字段设计

| 字段 | 含义 | 必填 | 说明 |
|---|---|---:|---|
| `province` | 省级行政区 | 是 | 与主面板省份名一致 |
| `city` | 城市名称 | 是 | 不得伪造，必须来自原始名录 |
| `city_id` | 城市唯一编码 | 是 | 建议使用行政区划代码或自建稳定 ID |
| `year` | 年份 | 是 | 2014–2022，与主面板一致 |
| `first_treat_year` | 首次处理年份 | 是 | 未处理为空 |
| `treated` | 当年是否处于处理状态 | 是 | `year >= first_treat_year` |
| `treatment_source` | 处理来源 | 是 | 政策名录/公告/平台记录 |
| `source_note` | 来源备注 | 是 | URL、文件名、页码或人工核验说明 |
| `aggregation_weight` | 上卷权重 | 是 | 默认 1；若按人口/城市权重，必须说明 |

### 执行命令草案

```powershell
python "scripts/build_city_year_treatment_registry.py" `
  --raw "data/raw_city_treatment_sources/" `
  --out "修改稿/v2说明文件/v2e/appendix_A0_city_year_treatment_registry.csv"
```

当前状态：仓库中未发现可直接作为原始城市处理名录的完整表；本轮只能生成字段设计和执行要求，未重跑，不得当作结果。

## 执行单元 B：province-year `treat_share` 聚合审计

### 输入文件

- `appendix_A0_city_year_treatment_registry.csv`
- 省份—城市隶属关系表
- v2d 已有 `appendix_A_treat_share_reconstruction_20260418.csv`

### 输出文件

- `appendix_A1_province_year_treat_share_audit.csv`
- `appendix_A2_treat_share_discrepancy_report.md`

### 审计逻辑

```python
province_year = (
    registry
    .groupby(["province", "year"])
    .agg(
        treated_city_count=("treated", "sum"),
        city_n=("city_id", "nunique"),
        weight_sum=("aggregation_weight", "sum"),
    )
)
province_year["treat_share_audit"] = (
    province_year["treated_city_count"] / province_year["city_n"]
)
```

### 风险点

- 行政区划变化会改变 `city_n`。
- 若 v2d 当前 `treat_share` 用的是非等权聚合，则必须披露权重。
- 若 audit 值与旧 `treat_share` 不一致，不得直接改正文结果，应先定位差异来源并重新 rerun。

## 执行单元 C：fresh rerun

### 输入文件

- `ppp论文数据/PPP_v3结果层状态表_20260413_1345.xlsx`
- `ppp论文数据/PPP_变量与模型最终采用口径表_20260413_1345.xlsx`
- `数据总表（一切数据基础）.xlsx`
- `PPP_empirical_reinforcement_bundle_20260416_unified_v3/00_unified_baseline_reference/scripts/build_unified_baseline_reference.py`
- `PPP_empirical_reinforcement_bundle_20260416_unified_v3/01_trend_adjusted_DID/scripts/run_trend_adjusted_did.py`
- `PPP_empirical_reinforcement_bundle_20260416_unified_v3/02_leave_one_province_out_jackknife/scripts/run_leave_one_province_out.py`
- `PPP_empirical_reinforcement_bundle_20260416_unified_v3/03_small_sample_inference_wild_cluster_bootstrap/scripts/summarize_small_sample_inference.py`
- `PPP_empirical_reinforcement_bundle_20260416_unified_v3/04_manuscript_integration/scripts/build_robustness_defense_summary.py`

### 轻量检查命令

```powershell
python -m py_compile "PPP_empirical_reinforcement_bundle_20260416_unified_v3/01_trend_adjusted_DID/scripts/run_trend_adjusted_did.py"
python -m py_compile "PPP_empirical_reinforcement_bundle_20260416_unified_v3/02_leave_one_province_out_jackknife/scripts/run_leave_one_province_out.py"
python -m py_compile "PPP_empirical_reinforcement_bundle_20260416_unified_v3/03_small_sample_inference_wild_cluster_bootstrap/scripts/summarize_small_sample_inference.py"
python -m py_compile "PPP_empirical_reinforcement_bundle_20260416_unified_v3/04_manuscript_integration/scripts/build_robustness_defense_summary.py"
```

### 完整 rerun 命令

```powershell
python "PPP_empirical_reinforcement_bundle_20260416_unified_v3/00_unified_baseline_reference/scripts/build_unified_baseline_reference.py"
python "PPP_empirical_reinforcement_bundle_20260416_unified_v3/01_trend_adjusted_DID/scripts/run_trend_adjusted_did.py"
python "PPP_empirical_reinforcement_bundle_20260416_unified_v3/02_leave_one_province_out_jackknife/scripts/run_leave_one_province_out.py"
python "PPP_empirical_reinforcement_bundle_20260416_unified_v3/03_small_sample_inference_wild_cluster_bootstrap/scripts/summarize_small_sample_inference.py"
python "PPP_empirical_reinforcement_bundle_20260416_unified_v3/04_manuscript_integration/scripts/build_robustness_defense_summary.py"
```

当前状态：本轮不运行完整 rerun；未重跑，不得当作结果。

## 执行单元 D：独立机制变量补强

### 候选机制变量

| 变量 | 数据源需求 | 机制含义 | 是否当前可用 |
|---|---|---|---|
| 审批时长 | 项目审批/入库时间戳 | 前端流程效率 | 未确认 |
| 采购到执行间隔 | 项目阶段时间戳 | 阶段转换效率 | 未确认 |
| 公告披露完整度 | 项目公告字段完整性 | 信息透明度 | 未确认 |
| 项目退库率 | 项目库状态变更 | 治理约束与筛选 | 未确认 |
| 在线服务指数 | 外部数字政府或政务服务指数 | 非文本制度环境 | 未确认 |
| 项目执行周期 | 项目起止/执行时间 | 执行衔接 | 未确认 |

写作原则：
- A/B/C/D 仍保留为政策文本证据线索。
- 只有非文本源机制变量完成数据构建并 rerun 后，才允许新增“独立机制补强”小节。

## 执行单元 E：文本变量效度审计

### 审计组件

1. 人工双标注样本：至少 80–120 篇文档。
2. 一致性统计：Cohen’s kappa 或 Krippendorff’s alpha。
3. 替代词典稳定性：A/B/C/D 替代词典省年聚合相关。
4. 主题稳定性：不同随机种子或主题数下的维度稳定。
5. 外部对照：与非文本治理指标或政策节点对照。

### 输出文件

- `appendix_G_manual_double_coding_template.csv`
- `appendix_G_text_validity_audit_report.md`
- `appendix_G_dictionary_stability.csv`

当前状态：未发现人工标注数据；本轮只能形成审计方案，未重跑，不得当作结果。

## 执行单元 F：文献嵌入

### 使用原则

- 不堆引用。
- 围绕四类顶刊防守动作组织：
  1. 原生处理名单；
  2. 外生政策时点；
  3. 结果变量与处理变量分源；
  4. 主识别、防守检验、边界诊断分层书写。

### 输出

- `v2e_literature_integration_patch.md`

## 执行单元 G：正文 patch

### 输出

- `v2e_manuscript_patch.md`

### 写法边界

允许写：
- 条件关联证据
- 防御性稳健性支持
- 边界性结果
- 政策文本证据线索
- 结构性改善

禁止写：
- 证明 PPP 显著提升治理质量
- 完全验证平行趋势
- 机制已被强证实的表述
- 稳健性检验构成新的主识别
- 治理绩效全面改善的强表述

---

## 2026-04-20 执行状态更新

根据用户人工确认，本轮已从“执行计划”推进到以下可审查资产：

1. 已生成 `appendix_A0` 至 `appendix_A4` 的派生 CSV/XLSX 模板；因无原始城市名单和阈值底表，模板保持空表头，不伪造记录。
2. `treat_share` 聚合审计默认采用等权城市计数 `aggregation_weight=1`，作为可替换审计基准，而非既有事实断言。
3. 已解析 14 篇 DID PDF 的本地元数据，输出 `v2e_DID_14_literature_metadata.*`；正式参考文献卷期页码仍待核验。
4. 已安装既有脚本运行依赖 `matplotlib`、`statsmodels`、`patsy`，未修改仓库依赖配置文件。
5. 已最小修改 `PPP_empirical_reinforcement_bundle_20260416_unified_v3/bundle_common.py`，修复 `.docx` 锚定歧义。
6. 已运行 baseline audit、trend-adjusted DID、leave-one-province-out、wild cluster bootstrap 和 robustness defense summary，日志见 `rerun_logs/`。
7. log-ratio 未发现可运行重估脚本，仍作为待补项；不得声称本轮已重估。

后续若进入正文 `.docx` 更新，应只 forward-apply `v2e_manuscript_patch.md` 中的谨慎段落，并继续以 `treat_share` TWFE 为唯一主识别。
