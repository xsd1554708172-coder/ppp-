# 第8部分 8.5 IV可行性评估（V2 四级十二类）

本轮基于 `PPP_3.6_model_ready_panel_v2_四级十二类_实际执行版.csv` 对若干候选 IV 做了可行性筛查。

## 候选变量
- dfi
- digital_econ
- base_station_density
- software_gdp_share
- it_service_gdp_share
- ln_rd_expenditure
- ln_tech_contract_value
- ln_patent_grants

## 评估逻辑
1. 用省—年 TWFE 检验候选 IV 对 `treat_share` 的第一阶段相关性；
2. 再用同口径回归查看候选 IV 对 `exec_share`、`proc_share`、`ppp_quality_zindex` 是否存在直接关联风险；
3. 只要“相关性不足”或“排他性担忧明显”任一成立，即不建议正式实施 IV。

## 本轮结果摘要
- 没有任何候选变量在第一阶段达到常用的显著性标准。
- `digital_econ` 对 `treat_share` 仅边际相关（p≈0.106），但对 `exec_share` 与 `proc_share` 存在直接关联，排他性不可信。
- `ln_tech_contract_value` 第一阶段几乎无相关性，同时对 `ppp_quality_zindex` 存在边际直接关联风险。
- 其余候选变量要么相关性很弱，要么缺乏足够的制度外生性论证。

## 当前最稳做法
本节作为“IV可行性评估后暂不强行实施”的增强识别方向保留，不正式进入 2SLS/IV 主结果。


## 2026-04-12 v3补充：8.5写作边界
- IV部分的工作量应体现在“候选变量筛查—排除—裁决”流程。
- 当前写法统一为“已评估暂不实施IV”，不要为了形式完整而硬做不可证伪工具变量。
