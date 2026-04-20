# v2e Empirical Rerun Checklist

本文件列出 `v2e` 真正进入实证执行阶段前必须核对的输入、脚本、输出与限制。当前文件原为 rerun checklist；2026-04-20 人工确认后，baseline / trend-adjusted DID / leave-one-province-out / wild / robustness summary 已实际运行。registry、log-ratio、独立机制、文本效度审计仍未重跑，不得当作结果。

## 1. 环境检查

本轮已检测：

| 组件 | 状态 | 影响 |
|---|---|---|
| Python | 可用：3.13.9 | 可执行抽取、轻量脚本检查 |
| `pandas` | 可用 | 可读 CSV/XLSX |
| `openpyxl` | 可用 | 可读写派生 XLSX，但本轮不改原始 XLSX |
| `python-docx` | 不可用 | 已改用 `zipfile + XML` 抽取 docx |
| `statsmodels` | 已安装并可用：0.14.6 | 支持既有 trend-adjusted DID 脚本运行 |
| `linearmodels` | 不可用 | 本轮既有脚本未使用；如需替代 panel FE 可另配 |
| R / Rscript | 未确认可用，`Rscript` 未找到 | R/fixest rerun 当前不可依赖 |
| `pandoc` | 未找到 | 不用于转换 docx |
| `soffice` | 未找到 | 不用于转换 docx |
| `aider.exe` | 可用 | 本轮未调用自动修改 |

## 2. source-of-truth 文件

必须存在且不得覆盖：

- `ppp论文数据/PPP_v3结果层状态表_20260413_1345.xlsx`
- `ppp论文数据/PPP_变量与模型最终采用口径表_20260413_1345.xlsx`
- `数据总表（一切数据基础）.xlsx`
- `修改稿/v2说明文件/v2d/appendix_A_treat_share_reconstruction_20260418.csv`
- `修改稿/v2说明文件/v2d/appendix_B_log_ratio_reestimate_20260418.csv`
- `PPP_empirical_reinforcement_bundle_20260416_unified_v3/`

## 3. city-year treatment registry

### 必须补齐的原始输入

- 城市处理名单
- 城市首次处理年份
- 处理认定来源
- 处理阈值或规则底表
- 城市到省份映射
- 年份范围 2014–2022 的行政区划处理

### registry 字段

```csv
province,city,city_id,year,first_treat_year,treated,treatment_source,source_note,aggregation_weight
```

### 审计检查

- 每个 `city_id-year` 是否唯一。
- `treated = 1[year >= first_treat_year]` 是否成立。
- 未处理城市的 `first_treat_year` 是否为空且 `treated=0`。
- 每个省年的 `city_n` 是否与行政区划一致。
- `aggregation_weight` 是否全部为 1；若不是，必须解释。

当前状态：仓库未显式提供完整城市级原始名录；未重跑，不得当作结果。

## 4. province-year aggregation audit

### 输出表字段

```csv
province,year,treated_city_count,city_n,weight_sum,treat_share_audit,treat_share_current,diff,flag
```

### flag 规则

- `OK`：差异绝对值小于 `1e-8`
- `ROUNDING`：差异小但可归因于四舍五入
- `MISMATCH`：差异需要回查城市名录、权重或省份映射
- `MISSING_SOURCE`：缺 city-year 源记录，不能审计

## 5. baseline TWFE

### 目标

重建第5.3节 baseline 结果，并与官方结果表核对。

### 需要输出

- `v2e_baseline_twfe_longtable.csv`
- `v2e_baseline_twfe_compare_to_official.md`

### 注意

- 主识别仍是 `treat_share` 多期 DID / TWFE。
- fresh rerun 若与官方结果不同，必须显式报告差异，不得静默替换。

当前状态：2026-04-20 已完成可运行模块重跑；具体模块状态以 `rerun_logs/rerun_status_summary.md` 为准。

## 6. trend-adjusted DID

### 可用脚本

```powershell
python "PPP_empirical_reinforcement_bundle_20260416_unified_v3/01_trend_adjusted_DID/scripts/run_trend_adjusted_did.py"
```

### 输出

- `trend_adjusted_did_results.xlsx`
- `trend_adjusted_did_body_insert.md`

### 写作边界

只作为省际异质趋势风险的防御性稳健性，不替代 baseline。

当前状态：2026-04-20 已运行成功；结果快照见 `v2e_rerun_result_snapshot.md`，写作仍限防御性稳健性。

## 7. leave-one-province-out

### 可用脚本

```powershell
python "PPP_empirical_reinforcement_bundle_20260416_unified_v3/02_leave_one_province_out_jackknife/scripts/run_leave_one_province_out.py"
```

### 输出

- `leave_one_province_out_results.xlsx`
- `leave_one_province_out_stability_summary.xlsx`
- `leave_one_province_out_body_insert.md`

### 写作边界

只回答是否由单一省份驱动，不构成新识别。

当前状态：2026-04-20 已完成可运行模块重跑；具体模块状态以 `rerun_logs/rerun_status_summary.md` 为准。

## 8. wild cluster bootstrap

### 可用脚本

```powershell
python "PPP_empirical_reinforcement_bundle_20260416_unified_v3/03_small_sample_inference_wild_cluster_bootstrap/scripts/summarize_small_sample_inference.py"
```

### 输出

- `wild_cluster_bootstrap_summary.xlsx`
- `small_sample_inference_body_insert.md`

### 写作边界

有限聚类下的保守推断边界支持，不得写成“结果更强”。

当前状态：2026-04-20 已完成可运行模块重跑；具体模块状态以 `rerun_logs/rerun_status_summary.md` 为准。

## 9. log-ratio / compositional robustness

### 已有资产

- `修改稿/v2说明文件/v2d/appendix_B_log_ratio_reestimate_20260418.csv`

### v2e 建议新增

- 执行/采购差值：`exec_share - proc_share`
- 执行/采购转换率或比率类指标
- fractional response / compositional 模型可行性评估

### 写作边界

构成性补强，不替代 share baseline。

当前状态：仓库未发现可直接运行的 log-ratio Python 脚本；本轮未生成新的 log-ratio rerun 结果，未重跑不得当作结果。

## 10. 独立机制变量

### 数据需求

| 变量 | 最低字段 |
|---|---|
| 审批时长 | `project_id,start_date,approval_date,province,year` |
| 采购到执行间隔 | `project_id,procurement_date,execution_date,province,year` |
| 公告披露完整度 | `project_id,required_fields,non_missing_fields,province,year` |
| 项目退库率 | `project_id,status,exit_date,province,year` |
| 在线服务指数 | `province,year,index_value,source` |
| 项目执行周期 | `project_id,execution_start,execution_end,province,year` |

当前状态：未构造，未重跑，不得当作结果。

## 11. 文本效度审计

### 人工标注模板字段

```csv
doc_id,province,year,coder_id,A_manual,B_manual,C_manual,D_manual,notes
```

### 统计

- Cohen’s kappa：二分类/多分类维度
- Krippendorff’s alpha：多编码员或缺失标注
- 替代词典稳定性：省年聚合相关与符号一致性
- 主题稳定性：不同随机种子/主题数下维度覆盖率

当前状态：缺人工双标注数据；未重跑，不得当作结果。

## 12. rerun 成功后同步清单

- 更新正文摘要数值。
- 更新第5.2、5.4、5.6节。
- 更新表4、表8、图8A/8B、附录D/F/G。
- 更新 `02_verification_report.md` 和 `03_delivery_note.md`。
- 若任一 fresh rerun 与 v2d 数值不一致，必须在说明文件中显式披露。


---

## 13. 2026-04-20 实际 rerun 更新

### 已执行并成功退出的模块

| 模块 | 结果 | 日志 |
|---|---|---|
| baseline unified reference | exit 0 | `rerun_logs/baseline_unified_reference.utf8.log` |
| trend-adjusted DID | exit 0 | `rerun_logs/trend_adjusted_DID.utf8.log` |
| leave-one-province-out | exit 0 | `rerun_logs/leave_one_province_out.utf8.log` |
| wild cluster bootstrap summary | exit 0 | `rerun_logs/wild_cluster_bootstrap_summary.utf8.log` |
| robustness defense summary | exit 0 | `rerun_logs/robustness_defense_summary.utf8.log` |

### 未执行或未能新生成的模块

- log-ratio：未找到可运行脚本，只发现既有 v2d/v2c/v1e 留底 CSV/说明。
- city-year registry：缺原始城市名单，已生成模板但未填数。
- treatment threshold audit：缺阈值底表，已生成模板但未填数。
- 独立机制变量：缺非文本源机制数据，已生成模板但未构造数值。
- 文本效度审计：缺人工双标注数据，已生成模板但未计算 kappa/alpha。

### 关键运行修复

- 安装运行时依赖：`matplotlib`、`statsmodels`、`patsy`。
- 最小修改 `PPP_empirical_reinforcement_bundle_20260416_unified_v3/bundle_common.py`：锚定 20260418 对象保留投稿版，解决 `.docx` 多重匹配。

### 输出快照

- `v2e_rerun_result_snapshot.csv`
- `v2e_rerun_result_snapshot.md`

正文引用时仍必须遵守：正式主识别是 `treat_share` 多期 DID / TWFE；防御性结果不得升级为主识别或“证明平行趋势”。

---

## 9. 省年审计数据与伪 registry 接入 full rerun 的使用边界（2026-04-20 19:26）

新增可用输入：

- `v2e_province_year_treat_share_audit_from_v2d.csv`：省年 treat_share 审计底表。
- `v2e_implied_city_slot_registry_from_v2d_treat_share.csv`：伪 city-slot registry，占位/审计用。

接入规则：

1. baseline TWFE 仍应优先使用正式省年面板和 source-of-truth 口径。
2. 若脚本需要 registry 层输入，只能将伪 registry 标记为 `implied_from_province_year_treat_share_reconstruction`。
3. 不得用伪 registry 估计或宣称真实城市层面 treatment effect。
4. 若后续找到真实城市名单或权重底表，应重建 registry 并与本次等权口径对比。



---

## Working proxy analysis update（2026-04-20 20:02:42）

- 已按人工确认使用 implied city-slot registry 与 province-year audit 生成 working proxy data outputs。
- 详见 `v2e_working_proxy_analysis_report.md` 与 `v2e_working_proxy_analysis_summary.json`。
- 机制变量与文本效度不由 registry/threshold 自动生成；已生成可得性矩阵并保留不能估计项。
