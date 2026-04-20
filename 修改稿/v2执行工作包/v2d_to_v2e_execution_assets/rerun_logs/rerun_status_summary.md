# v2e full rerun 状态汇总

> 状态：本轮已按用户授权安装既有脚本所需运行时依赖，并完成 full rerun 尝试；log-ratio 未找到可直接运行脚本。未重跑，不得当作结果仅适用于未成功模块。

| module | status | exit_code | reason | log |
|---|---|---:|---|---|
| baseline_unified_reference | success | 0 |  | `C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\修改稿\v2执行工作包\v2d_to_v2e_execution_assets\rerun_logs\baseline_unified_reference.utf8.log` |
| trend_adjusted_DID | success | 0 |  | `C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\修改稿\v2执行工作包\v2d_to_v2e_execution_assets\rerun_logs\trend_adjusted_DID.utf8.log` |
| leave_one_province_out | success | 0 |  | `C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\修改稿\v2执行工作包\v2d_to_v2e_execution_assets\rerun_logs\leave_one_province_out.utf8.log` |
| wild_cluster_bootstrap_summary | success | 0 |  | `C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\修改稿\v2执行工作包\v2d_to_v2e_execution_assets\rerun_logs\wild_cluster_bootstrap_summary.utf8.log` |
| robustness_defense_summary | success | 0 |  | `C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\修改稿\v2执行工作包\v2d_to_v2e_execution_assets\rerun_logs\robustness_defense_summary.utf8.log` |
| log_ratio | no_runnable_script_found | NA | python scripts found: 0 | `C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\修改稿\v2执行工作包\v2d_to_v2e_execution_assets\rerun_logs\log_ratio_search.utf8.log` |

## 本轮可认定事项

- 已安装 `matplotlib-3.10.8`、`statsmodels-0.14.6`、`patsy-1.0.2`，原因是 trend-adjusted DID 与 leave-one-province-out 既有脚本直接依赖这些包；未修改仓库依赖配置文件。
- 已对 `bundle_common.resolve_paths` 做最小修复，将 `current_docx` 锚定为根目录 20260418 对象保留投稿版，避免多个 `.docx` 触发歧义。
- baseline、trend-adjusted DID、leave-one-province-out、wild cluster bootstrap、robustness defense summary 均已真实运行并退出码为 0。
- `robustness_defense_summary` 汇总的是上述已重跑模块的当前输出。
- log-ratio：仓库中仅发现既有留底 CSV/说明，未发现可直接运行的 Python 重估脚本，因此未生成新的 log-ratio rerun 结果。

## 正文使用边界

- 成功重跑不自动等于可强化结论；仍需与正式口径表逐项核对。
- trend-adjusted DID、leave-one-province-out、wild cluster bootstrap 只能写作防御性稳健性或边界诊断，不能替代 `treat_share` TWFE 主识别。
- log-ratio 当前只能引用既有留底或作为待补 rerun 项，不能声称本轮已重估。
