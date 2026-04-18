# 第8部分 8.4 matched-sample DID / PSM-DID 说明（V2 四级十二类）

本轮结果基于新版 `PPP_3.6_model_ready_panel_v2_四级十二类_实际执行版.csv`。

## 方法定位
本部分按你既定口径写成 **matched-sample DID / TWFE**，不夸写为理想型经典 PSM-DID。

## 匹配做法
- 单位：省级
- 处理定义：`ever_treated = max(did_any)`
- 倾向得分使用处理前（post=0）均值协变量估计
- 协变量：dfi、digital_econ、base_station_density、ln_rd_expenditure、ln_patent_grants、ppp_doc_n
- 匹配方式：最近邻匹配（without replacement）
- 共同支持样本：4 个 treated 省份 + 4 个 control 省份

## 结果阅读
- 由于从未处理省级单元仅 4 个，共同支持区域较窄；
- 匹配后平衡性改善有限，若干变量 SMD 仍偏高；
- 因此本部分更适合作为**审慎性稳健性补充**，不宜替代第5部分主识别结果。

## 主要结果
- `treat_share -> exec_share`: -0.7325, p=0.2384
- `treat_share -> proc_share`: 0.8974, p=0.1075
- `did_any -> exec_share`: 0.0216, p=0.8714
- `did_any -> proc_share`: -0.1365, p=0.1739

## 写作建议
可以写成：
> 在 matched-sample DID/TWFE 的补充检验中，由于可用于匹配的未处理省级样本较少，共同支持区域相对有限，匹配后结果方向存在波动，说明第8.4更适合作为审慎性稳健性补充，而不宜替代主识别结果。


## 2026-04-12 v3补充：8.4写作边界
- 只写为 matched-sample DID/TWFE 的审慎补充。
- 共同支持域较窄、匹配后样本较小，应主动交代，不应夸写为理想型经典PSM-DID。
