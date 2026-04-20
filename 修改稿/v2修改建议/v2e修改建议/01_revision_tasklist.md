# v2e Revision Tasklist

本清单把 `v2d_DID_冲刺修订报告` 转换为 `v2e` 可执行任务。除非有 fresh rerun 输出，否则任何新增实证项均为“未重跑，不得当作结果”。

## P0：必须先做的硬证据链任务

| 优先级 | 任务 | 输入 | 产出 | 当前状态 | 红线 |
|---|---|---|---|---|---|
| P0 | 重建 city-year treatment registry | 原始城市改革名录、政策批次、处理阈值底表 | `appendix_A0_city_year_treatment_registry.csv/xlsx` | 当前缺原始名录，只能先设计字段与模板 | 不伪造城市名单 |
| P0 | 省年 `treat_share` 聚合审计 | city-year registry、行政区划年份表、聚合权重规则 | `appendix_A1_province_year_treat_share_audit.csv` | 需数据补齐后运行 | 不直接改旧 `treat_share` |
| P0 | 全链 fresh rerun | 官方主面板、baseline long table、补强包脚本 | 新 baseline / trend / leave-one-out / wild / log-ratio 长表与摘要表 | 2026-04-20 已重跑 baseline/trend/leave-one/wild/summary；log-ratio 无脚本未重跑 | log-ratio 未重跑不得当作结果 |
| P0 | 独立机制变量补强 | 非文本机制数据：审批时长、采购到执行间隔、披露完整度、退库率、在线服务指数 | 新机制数据字典、机制结果表、机制节 patch | 当前仅能设计变量与数据需求 | 不把 A/B/C/D 写成强机制 |
| P0 | 文本变量效度审计 | 文档级文本变量、人工双标注样本、替代词典、主题模型稳定性输出 | `appendix_G_text_validity_audit.*` | 当前缺人工标注，只能生成审计方案 | 不用自动指标冒充人工一致性 |

## P1：识别防守与文献嵌入任务

| 优先级 | 任务 | 输入 | 产出 | 当前状态 | 红线 |
|---|---|---|---|---|---|
| P1 | cohort / stack / placebo / randomization diagnostics | main panel、city-year registry、脚本 | 附录诊断页、随机化分布图 | 当前未运行 | 只能作为边界诊断 |
| P1 | 识别服务型图表 | registry、样本流、估计结果长表 | treatment timing 图、样本流图、coefficient plot | 当前未生成 | 不做装饰性图 |
| P1 | 14 篇 DID 文献嵌入 | `did参考文献补充/` 与 v2d 报告摘要 | 第2章、第4章 patch | 本轮生成 patch | 不编造页码和模型细节 |
| P1 | share outcome 构成性补强扩展 | 正式主样本 | log-ratio 扩展、执行-采购差值、转换率、fractional/Dirichlet 备选 | 当前只复用已有 log-ratio | 不替代主模型 |

## P2：文稿与版本同步任务

| 优先级 | 任务 | 输入 | 产出 | 当前状态 | 红线 |
|---|---|---|---|---|---|
| P2 | v2e clean manuscript 语言精修 | 所有 rerun 后结果 | `v2e` 正文稿 | 本轮只给 patch，不直接改 docx | 不在 rerun 前美化成最终稿 |
| P2 | v1/v2 口径同步 | v2e 口径、v1 当前版本 | v1e mirror note | 本轮不处理 v1 | 不让 v1 支配 v2 |
| P2 | 参考文献格式全量清理 | 14 篇 DID PDF 与原参考文献 | references patch | 本轮只给嵌入建议 | 不编造卷期页码 |

## 本轮已完成

- 已解析本地 `v2d_DID_冲刺修订报告_可下载版.docx`。
- 已抽取 `extracted.md`。
- 已生成 v2e 执行计划、正文 patch、rerun checklist、文献嵌入 patch。

## 本轮未完成

- 未完成 city-year treatment registry 的真实填充。
- 原始 planning 阶段未完成全链 fresh rerun；2026-04-20 人工确认后已完成 baseline / trend-adjusted DID / leave-one-province-out / wild / robustness summary 重跑，log-ratio 因无可运行脚本仍未重跑。
- 未完成独立机制变量数据采集。
- 未完成人工文本双标注与一致性统计。
- 未生成新的 manuscript-facing `docx`。

---

## 2026-04-20 人工确认后的执行更新

| 任务 | 更新状态 | 证据文件 | 仍需注意 |
|---|---|---|---|
| city-year treatment registry | 已生成空 CSV/XLSX 模板与 codebook；未填入城市名单 | `appendix_A0_city_year_treatment_registry_template.csv/.xlsx`；`appendix_A0_A4_templates_codebook.md` | 用户确认无原始城市名单；不得伪造 |
| 省年 `treat_share` 聚合审计 | 已生成审计模板；默认审计假设为等权城市计数 `aggregation_weight=1` | `appendix_A1_province_year_treat_share_audit_template.csv/.xlsx`；`appendix_A2_treat_share_aggregation_audit_note.md` | 该假设是默认审计口径，不是已证实历史口径 |
| 处理阈值底表 | 已生成阈值审计模板；未填入阈值 | `appendix_A2_treatment_threshold_audit_template.csv/.xlsx` | 用户确认当前无阈值底表 |
| 独立机制变量 | 已生成变量设计模板 | `appendix_A3_independent_mechanism_variable_template.csv/.xlsx` | 仍需真实非文本数据 |
| 文本效度审计 | 已生成审计模板 | `appendix_A4_text_validity_audit_template.csv/.xlsx` | 仍需人工双标注数据 |
| 14 篇 DID 文献 | 已执行本地 PDF 元数据提取 | `v2e_DID_14_literature_metadata.csv/.json/.md` | 卷期页码仍需人工/数据库核验 |
| full rerun | baseline、trend-adjusted DID、leave-one-province-out、wild、robustness summary 已真实运行；log-ratio 未找到可运行脚本 | `rerun_logs/rerun_status_summary.md`；`v2e_rerun_result_snapshot.csv/.md` | 成功运行不自动替代正式正文口径 |
| 运行环境 | 已安装 `matplotlib`、`statsmodels`、`patsy` 以执行既有脚本 | pip 输出见本轮终端记录；状态写入 rerun summary | 未修改仓库依赖配置 |

---

## 2026-04-20 执行更新：省年审计与 implied registry

- 已完成：从 v2d 省年 treat_share 重构表生成 `v2e_province_year_treat_share_audit_from_v2d.*`。
- 已完成：在无原始城市名单和阈值底表情况下，按等权 city-slot 生成 `v2e_implied_city_slot_registry_from_v2d_treat_share.*`。
- 已完成：补写 `v2e_implied_registry_construction_report.md`，明确“可用但非原始 registry”的边界。
- 仍待 full rerun：将派生审计表接入正式 rerun 脚本前，需在日志中标明 implied audit data，不得写作真实 city-year registry。
