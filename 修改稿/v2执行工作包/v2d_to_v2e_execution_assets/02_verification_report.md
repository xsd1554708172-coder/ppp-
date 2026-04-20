# v2e Verification Report

验证日期：2026-04-20

> 本报告验证的是 `v2e` 修订规划资产、派生模板、DID 文献元数据提取与 2026-04-20 full rerun 尝试。凡明确标记为已重跑的模块可作为审计快照；log-ratio 与未填充模板仍为“未重跑，不得当作结果”。

## 1. 输入读取验证

| 项目 | 状态 |
|---|---|
| `AGENTS.md` | 已读取 |
| `README_工作区导航.md` | 已读取 |
| 本地 `v2d_DID_冲刺修订报告_可下载版.docx` | 已读取，470 个正文段落 |
| `v2d修改建议` 下 `.md/.txt/.docx` | 已扫描；当前只有该 `docx` |
| v2d 说明文件与 manuscript-facing markdown | 已读取/定位 |
| empirical reinforcement bundle README | 已读取 |
| trend / leave-one-out / wild / manuscript integration 脚本 | 已定位 |
| DID 参考文献补充目录 | 已检测 14 篇 PDF |

## 2. 环境验证

| 组件 | 状态 |
|---|---|
| Git 仓库 | 是 |
| 当前分支 | `main` |
| Python | 可用 |
| `pandas` | 可用 |
| `openpyxl` | 可用 |
| `python-docx` | 不可用，已用 zip/XML 解析替代 |
| `statsmodels` | 已安装并可用：0.14.6 |
| `linearmodels` | 不可用；本轮既有脚本未使用 |
| `pandoc` / `soffice` | 不可用 |
| `aider.exe` | 可用但未调用 |

## 3. 本轮已完成的资产

- `修改稿/v2修改建议/v2d修改建议/_codex_extracts/v2d_DID_冲刺修订报告_extracted.md`
- `修改稿/v2执行工作包/v2d_to_v2e_execution_assets/00_input_mapping.md`
- `修改稿/v2执行工作包/v2d_to_v2e_execution_assets/01_revision_tasklist.md`
- `修改稿/v2执行工作包/v2d_to_v2e_execution_assets/02_verification_report.md`
- `修改稿/v2执行工作包/v2d_to_v2e_execution_assets/03_delivery_note.md`
- `修改稿/v2执行工作包/v2d_to_v2e_execution_assets/v2e_DID_冲刺修订执行计划.md`
- `修改稿/v2执行工作包/v2d_to_v2e_execution_assets/v2e_manuscript_patch.md`
- `修改稿/v2执行工作包/v2d_to_v2e_execution_assets/v2e_empirical_rerun_checklist.md`
- `修改稿/v2执行工作包/v2d_to_v2e_execution_assets/v2e_literature_integration_patch.md`

## 3.1 本轮实际运行的验证命令

已运行：

```powershell
python -m py_compile "PPP_empirical_reinforcement_bundle_20260416_unified_v3/01_trend_adjusted_DID/scripts/run_trend_adjusted_did.py" "PPP_empirical_reinforcement_bundle_20260416_unified_v3/02_leave_one_province_out_jackknife/scripts/run_leave_one_province_out.py" "PPP_empirical_reinforcement_bundle_20260416_unified_v3/03_small_sample_inference_wild_cluster_bootstrap/scripts/summarize_small_sample_inference.py" "PPP_empirical_reinforcement_bundle_20260416_unified_v3/04_manuscript_integration/scripts/build_robustness_defense_summary.py"
```

结果：退出码 `0`，表示上述脚本可通过 Python 语法编译检查。该命令不是实证重跑；未重跑，不得当作结果。

已运行：

```powershell
git diff --stat
git status --short --branch
git diff --no-index --stat -- NUL <new-file>
git diff --no-index --check -- NUL "修改稿/v2执行工作包/v2d_to_v2e_execution_assets/v2e_manuscript_patch.md"
```

结果：
- `git diff --stat` 对未跟踪文件为空。
- `git status --short --branch` 显示本轮新增两个未跟踪目录：`v2d修改建议/_codex_extracts/` 与 `v2e修改建议/`。
- `git diff --no-index --stat` 已确认 9 个新增文本文件均可用 diff 审查。
- `git diff --no-index --check` 未报告 whitespace error，仅提示未来 Git 可能把 LF 转 CRLF。

## 4. 未完成且不得替代的事项

- 未填充真实 city-year treatment registry。
- 未完成省年 `treat_share` 聚合审计。
- 已运行 baseline TWFE audit rerun、trend-adjusted DID、leave-one-province-out、wild cluster bootstrap 与 robustness defense summary。
- 未运行 log-ratio fresh rerun；仓库未发现可运行脚本。
- 未扩展 log-ratio 之外的 compositional robustness。
- 未构造独立机制变量。
- 未完成人工双标注或文本效度统计。
- 未生成新的 `v2e` manuscript-facing `.docx`。

## 5. 学术红线检查

| 红线 | 检查结果 |
|---|---|
| `treat_share` 多期 DID / TWFE 仍是唯一主识别 | PASS |
| 未把 trend / leave-one-out / wild / log-ratio 写成主识别 | PASS |
| 未把 event study 写成证明平行趋势 | PASS |
| 未把 `ppp_quality_zindex` 写成治理质量全面提升 | PASS |
| 未把 A/B/C/D 写成强机制 | PASS |
| 新系数均来自本轮 rerun 快照；未编造系数、显著性或图表内容 | PASS |
| 未修改原始 `.docx` / 原始数据 `.xlsx`；重跑覆盖了补强包派生输出表，并最小修改了 `bundle_common.py` 路径锚定 | PASS |

## 6. 人工确认状态

用户已在 2026-04-20 明确确认：

1. 当前无 city-year treatment registry 原始城市名单。
2. 当前无处理阈值底表。
3. `treat_share` 省年聚合权重未知；本轮按等权城市计数设置审计默认权重。
4. 允许生成派生 CSV/XLSX 模板。
5. rerun 环境未知但允许为文章需要执行必要操作；本轮已安装必要运行时依赖。
6. 需要逐篇解析 14 篇 DID PDF 的正式参考文献元数据；本轮完成轻量元数据提取，正式卷期页码仍待核验。
7. 允许进入 full rerun；本轮已完成可运行模块重跑。

## 7. 结论

本轮已完成 `v2e` 的 planning / patch / checklist 资产，并在人工确认后执行 full rerun：baseline、trend-adjusted DID、leave-one-province-out、wild cluster bootstrap 与 robustness summary 均成功；log-ratio 因未发现可运行脚本仍未重跑。所有未重跑内容已明确标记。


---

## 8. 2026-04-20 人工确认后新增验证

### 8.1 派生模板验证

已生成以下派生 CSV/XLSX 模板，均为空表头模板，未填入或伪造城市名单、阈值、机制数值或文本标注：

- `appendix_A0_city_year_treatment_registry_template.csv/.xlsx`
- `appendix_A1_province_year_treat_share_audit_template.csv/.xlsx`
- `appendix_A2_treatment_threshold_audit_template.csv/.xlsx`
- `appendix_A3_independent_mechanism_variable_template.csv/.xlsx`
- `appendix_A4_text_validity_audit_template.csv/.xlsx`

默认聚合审计假设：在没有权重底表时，采用等权城市计数 `aggregation_weight=1` 作为审计基准；这不是声称原论文已按等权构造。

### 8.2 DID 文献解析验证

已对 `ppp论文数据/参考文献/did参考文献补充/` 下 14 篇 PDF 执行 PyPDF2 元数据与前 3 页轻量文本提取，输出：

- `v2e_DID_14_literature_metadata.csv`
- `v2e_DID_14_literature_metadata.json`
- `v2e_DID_14_literature_metadata_report.md`

限制：未联网核验卷期页码和正式参考文献格式；不得编造缺失元数据。

### 8.3 full rerun 验证

已安装当前既有脚本所需运行时依赖 `matplotlib`、`statsmodels`、`patsy`，未修改仓库依赖配置文件。已最小修改：

- `PPP_empirical_reinforcement_bundle_20260416_unified_v3/bundle_common.py`

修改目的：将 `current_docx` 锚定为根目录 `PPP论文_完整论文初稿_公共管理风格_顶刊冲刺整合稿_20260418_对象保留投稿版.docx`，避免多个 `.docx` 文件导致 rerun 脚本歧义失败。

rerun 状态见：

- `rerun_logs/rerun_status_summary.md`
- `rerun_logs/*.utf8.log`
- `v2e_rerun_result_snapshot.csv`
- `v2e_rerun_result_snapshot.md`

结论：baseline、trend-adjusted DID、leave-one-province-out、wild cluster bootstrap、robustness defense summary 退出码均为 0；log-ratio 未发现可运行脚本，仍未重跑。

### 8.4 数值边界验证

- `exec_share`：trend-adjusted 后方向仍正但不显著；wild p = 0.076，必须写作统计强度敏感。
- `proc_share`：trend-adjusted 后仍负且 p = 0.048；wild p = 0.122，不能写作“所有检验更强”。
- `ppp_quality_zindex`：trend-adjusted 后不稳定，wild p = 0.237，继续不得抬升为主结论。
- baseline audit 与 official anchor 接近但未达 `1e-6` 完全一致容差；正文仍以正式口径表为准。



---

## 9. 最终 fresh verification（2026-04-20）

已重新运行以下核查命令：

```powershell
python -m py_compile "PPP_empirical_reinforcement_bundle_20260416_unified_v3/bundle_common.py" "PPP_empirical_reinforcement_bundle_20260416_unified_v3/00_unified_baseline_reference/scripts/build_unified_baseline_reference.py" "PPP_empirical_reinforcement_bundle_20260416_unified_v3/01_trend_adjusted_DID/scripts/run_trend_adjusted_did.py" "PPP_empirical_reinforcement_bundle_20260416_unified_v3/02_leave_one_province_out_jackknife/scripts/run_leave_one_province_out.py" "PPP_empirical_reinforcement_bundle_20260416_unified_v3/03_small_sample_inference_wild_cluster_bootstrap/scripts/summarize_small_sample_inference.py" "PPP_empirical_reinforcement_bundle_20260416_unified_v3/04_manuscript_integration/scripts/build_robustness_defense_summary.py"
git diff --check
git diff --stat
git status --short --branch
```

结果：

- `py_compile_exit=0`。
- `git diff --check` 退出码 `0`。
- `rerun_status_summary_utf8.csv` 显示 baseline、trend-adjusted DID、leave-one-province-out、wild cluster bootstrap、robustness defense summary 均为 `success`；log-ratio 为 `no_runnable_script_found`。
- 当前 Git 工作区包含：
  - 1 个脚本锚定修复：`PPP_empirical_reinforcement_bundle_20260416_unified_v3/bundle_common.py`；
  - 1 个 baseline note anchor 更新：`00_unified_baseline_reference/notes/baseline_spec_readme.md`；
  - 6 个 rerun 派生 `.xlsx` 输出变更；
  - 12 个新生成的 Figure 8A/8B rerun 图形文件；
  - v2d docx 抽取目录与 v2e 执行资产目录；
  - 一个本轮开始前已存在的未跟踪 `did补充文献.zip`。

未执行 commit，未 push。

---

## 10. 省年审计数据与伪 city-slot registry 生成验证（2026-04-20 19:26）

- 已生成位置：`C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\修改稿\v2执行工作包\v2d_to_v2e_execution_assets`。
- 省年审计数据：`v2e_province_year_treat_share_audit_from_v2d.csv` / `v2e_province_year_treat_share_audit_from_v2d.xlsx`。
- 伪 city-slot registry：`v2e_implied_city_slot_registry_from_v2d_treat_share.csv` / `v2e_implied_city_slot_registry_from_v2d_treat_share.xlsx`。
- 独立说明文件：`v2e_implied_registry_construction_report.md`。
- 机器可读摘要：`v2e_implied_registry_construction_summary.json`。
- 输入依据为 v2d 已落地的 `appendix_A_treat_share_reconstruction_20260418.csv` 和省级处理时点表；未修改原始数据总表、未修改任何原始 `.xlsx` 或 `.docx`。
- 构造口径：在无真实城市名单、无阈值底表、无权重底表情况下，采用等权 implied city-slot；该设定与 `treated_city_count_implied = treat_share * city_n` 的省年计数份额口径一致。
- 核验结果：省年行数 266，slot 行数 2870；`flag` 计数为 {'OK': 258, 'MISSING_CITY_N': 8}；非缺失行 slot 回聚合误差最大值 8.327e-17。
- 重要限制：这些文件是审计/占位用派生资产，不能替代真实 city-year treatment registry，不能据此新增城市层面因果结论。



---

## Working proxy analysis update（2026-04-20 20:02:42）

- 已按人工确认使用 implied city-slot registry 与 province-year audit 生成 working proxy data outputs。
- 详见 `v2e_working_proxy_analysis_report.md` 与 `v2e_working_proxy_analysis_summary.json`。
- 机制变量与文本效度不由 registry/threshold 自动生成；已生成可得性矩阵并保留不能估计项。
