# v2e implied city-slot registry 构造报告

> 生成时间：2026-04-20 19:28
> 定位：本文件说明“可用的省年审计数据”和“伪 city-slot registry”的构造依据、字段口径、可用边界与风险。
> 重要边界：这些文件是从 v2d 已落地的省年 treat_share 重构表反推得到的**派生审计资产**，不是原始城市处理名录，也不是处理阈值底表。

## 1. 放置位置

本轮所有新生成的审计资产均放在 v2d_to_v2e 执行工作包目录：

`C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\修改稿\v2执行工作包\v2d_to_v2e_execution_assets`

理由：本轮目标是为 v2d → v2e 的 DID 冲刺修订提供可审查、可 Git diff 的派生资产；不覆盖 v2d 原始资产，不写入原始数据目录，不修改任何 `.docx` 或 `.xlsx` 主数据文件。

## 2. 输入文件

- 省年 treat_share 重构表：`C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\修改稿\v2说明文件\v2d\appendix_A_treat_share_reconstruction_20260418.csv`
- 省级处理时点表：`C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\修改稿\v2说明文件\v2d\appendix_A_province_treatment_timing_20260418.csv`
- 用户确认：无原始 city-year treatment registry 城市名单；无处理阈值底表；允许下一轮生成派生 CSV/XLSX 模板；允许进入 full rerun 阶段。

## 3. 输出文件

### 3.1 可用的省年审计数据

- CSV：`C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\修改稿\v2执行工作包\v2d_to_v2e_execution_assets\v2e_province_year_treat_share_audit_from_v2d.csv`
- XLSX：`C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\修改稿\v2执行工作包\v2d_to_v2e_execution_assets\v2e_province_year_treat_share_audit_from_v2d.xlsx`

用途：审计 province-year 层级的 `treat_share_current`、`treated_city_count_implied_source`、`did_intensity_current`、`post`、`did_any_current` 等是否内部一致，并为后续 full rerun 前的处理强度口径复核提供底表。

### 3.2 伪 city-slot registry

- CSV：`C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\修改稿\v2执行工作包\v2d_to_v2e_execution_assets\v2e_implied_city_slot_registry_from_v2d_treat_share.csv`
- XLSX：`C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\修改稿\v2执行工作包\v2d_to_v2e_execution_assets\v2e_implied_city_slot_registry_from_v2d_treat_share.xlsx`

用途：在没有原始城市名单时，将每个 province-year 的 `city_n` 展开为 `IMPLIED_SLOT_###`，并用 `treated_city_count_implied_source` 标记前若干 slot 的覆盖状态，从而形成可审计的“省内城市席位”处理登记表。该表只能用于聚合链条审计、脚本接口测试或 rerun 前的数据结构占位，不能在论文中写成真实城市名单。

### 3.3 机器可读摘要

- JSON：`C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\修改稿\v2执行工作包\v2d_to_v2e_execution_assets\v2e_implied_registry_construction_summary.json`

用途：记录生成脚本得到的行数、误差、flag 计数和输入输出路径，便于后续自动核验。

## 4. 构造口径

1. 以 `appendix_A_treat_share_reconstruction_20260418.csv` 为唯一直接数据来源。
2. 省年层保持原有 `province`、`year`、`city_n`、`treat_share`、`treated_city_count_implied`、`post`、`did_intensity` 等字段，并在审计表中映射为 `treat_share_current`、`treated_city_count_implied_source`、`did_intensity_current`。
3. 在非缺失 `city_n` 且 `city_n > 0` 的省年单元内，生成 `city_n` 个伪城市席位：`IMPLIED_SLOT_001`、`IMPLIED_SLOT_002`……。
4. 将 `treated_city_count_implied_source` 四舍五入为整数后，用前 N 个 slot 表示被覆盖席位：`treatment_coverage_slot = 1`，其余为 0。
5. DID 生效口径为：`treated = treatment_coverage_slot * post`；伪 registry 中同步记录 `did_active_implied`。
6. 聚合权重设置为：`aggregation_weight = 1`，即省内城市 slot 等权计数。
7. 等权理由：当前仓库未发现原始城市名单、人口/财政/项目量权重底表或阈值底表；同时 v2d 重构表中 `treated_city_count_implied = treat_share * city_n`，表明现有 treat_share 更接近“城市计数份额”而非加权份额。因此，等权 city-slot 是在当前证据下最保守、最可审计的派生设定。
8. 阈值字段统一标记为 `not_available_no_threshold_table`；不得据此补写真实阈值来源。

## 5. 审计结果摘要

- 省年审计行数：266
- 伪 city-slot registry 行数：2870
- 重构表省份数：32
- 年份范围：2014–2022
- `flag` 计数：
- `OK`：258
- `MISSING_CITY_N`：8
- `city_n` 发生变化的省份：吉林、山东、海南、湖北、湖南
- 非缺失行 `treat_share_current` 回算最大绝对误差：8.327e-17
- 非缺失行由 slot 回聚合的 `slot_treat_share` 最大绝对误差：8.327e-17
- 非缺失行 `did_intensity_current` 回算最大绝对误差：8.327e-17

## 6. 字段说明

### 6.1 省年审计表核心字段

- `province`、`year`：省年单元。
- `city_n`：v2d 重构表中记录的省内城市数。
- `eligible_city_count`：用于等权审计的有效城市计数，当前等于 `city_n`。
- `treated_city_count_implied_source`：由 v2d 重构表提供的隐含处理城市数。
- `treated_city_count_integer`：对隐含处理城市数四舍五入后的整数席位数。
- `treat_share_current`：v2d 重构表中的处理强度。
- `treat_share_recomputed_from_integer_count`：`treated_city_count_integer / eligible_city_count`。
- `difference`：当前 treat_share 与整数回算份额之间的差值。
- `did_intensity_current`：v2d 重构表中的 DID 强度。
- `did_intensity_recomputed`：`post * treat_share_recomputed_from_integer_count`。
- `did_intensity_difference`：当前 DID 强度与回算 DID 强度之间的差值。
- `aggregation_rule`：当前为 `equal_city_count_implied_from_province_year_treat_share`。
- `threshold_rule`：当前为 `not_available_no_threshold_table`。
- `flag`：`OK` 表示当前省年可由 city_n 和整数席位重构；`MISSING_CITY_N` 表示 city_n 缺失，未生成 slot。
- `flag_note`：说明该行的审计/缺失原因。
- `slot_rows`、`slot_weight_sum`、`slot_coverage_sum`、`slot_active_sum`：从伪 city-slot registry 回聚合的辅助计数。
- `slot_treat_share`、`slot_did_intensity`、`slot_share_difference`、`slot_did_difference`：slot 层回聚合校验字段。

### 6.2 伪 city-slot registry 核心字段

- `province`、`year`：省年单元。
- `city`：伪城市席位编号，例如 `IMPLIED_SLOT_001`，不是现实城市名。
- `city_id`：`IMPLIED::<province>::###`，不是现实城市代码。
- `first_treat_year`：若该省有省级处理时点，则沿用；否则为空。
- `treated`：post 后处于处理覆盖席位的 DID 状态。
- `treatment_coverage_slot`：是否属于省年内被 treat_share 覆盖的席位。
- `did_active_implied`：与 `treated` 同步的 implied DID 激活字段，便于脚本识别。
- `treatment_source`：统一标记为 `implied_from_province_year_treat_share_reconstruction`。
- `source_note`：说明该行不是原始城市名单。
- `aggregation_weight`：等权设为 1。
- `city_n_source`、`treated_city_count_implied_source`、`treat_share_source`、`did_intensity_source`：来自 v2d 省年重构表的原始省年口径。
- `threshold_rule`：统一标记为无阈值底表。
- `source_file`：生成该行所依据的 v2d 重构 CSV。

## 7. 可用于论文/实证的方式

可以使用：

1. 作为附录 A 的“省年 treat_share 聚合审计表”。
2. 作为 full rerun 前的处理强度链条复核底表。
3. 作为脚本接口测试或审计占位表，检查 province-year 聚合是否可从 slot 层回算。
4. 在正文中谨慎表述为“基于省年重构表的 implied city-slot audit”，用于提升透明度。

不可以使用：

1. 不得写成真实城市名单或真实 city-year treatment registry。
2. 不得据此声称已经恢复原始处理阈值。
3. 不得据此新增城市层面的因果结论。
4. 不得把伪 slot 的数量、顺序或 first slot 标记解释为真实城市排序。
5. 不得把这些派生文件替代原始数据总表或正式 source-of-truth xlsx。

## 8. 后续 full rerun 前必须确认

1. 若找到真实城市名单，应以真实 `city`/`city_id` 替换伪 slot，并保留本次表作为审计留痕。
2. 若找到人口、财政、项目量等权重底表，应另建加权口径并与当前等权口径并列比较。
3. 若找到处理阈值底表，应补充 `threshold_rule`、`threshold_value`、`threshold_source` 等字段。
4. 若 full rerun 采用这些派生表，必须在结果说明中标注“implied audit data”，不能写作原始 registry。
