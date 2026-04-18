# 第8部分 8.6 DML 高维稳健性检验（V2 四级十二类）

## 文件说明
- 结果文件：`PPP_第8部分_8.6DML稳健性检验_V2_四级十二类_实际执行版.xlsx`
- 汇总表：`PPP_第8部分_8.6DML结果汇总_V2_四级十二类_实际执行版.csv`

## 方法口径
- 处理变量：`treat_share`
- 结果变量：`exec_share`、`proc_share`、`ppp_quality_zindex`
- 高维控制：经济基础变量 + 四级十二类文本指数 + 24 个 topic share + province/year 哑变量
- 估计方式：5-fold cross-fitting 的部分线性 DML
- nuisance model：LassoCV
- 最终阶段：残差化后线性回归，按 province 聚类稳健标准误

## 核心结果
### exec_share
- DML 系数：0.2985
- p 值：0.0024
- baseline TWFE：0.3556

### proc_share
- DML 系数：-0.2720
- p 值：0.0034
- baseline TWFE：-0.4023

### ppp_quality_zindex
- DML 系数：0.7198
- p 值：0.0018
- baseline TWFE：0.5253

## 结果阅读建议
- `exec_share` 与 `proc_share` 在 DML 下方向与 baseline TWFE 一致，说明推进结构结论在高维控制设定下仍然成立。
- `ppp_quality_zindex` 在 baseline TWFE 中不显著，但在 DML 下转为显著正向，说明高维控制设定下存在“质量型结果改善”的补充信号。
- 正文写法仍应保持克制：DML 作为高维稳健性支持，不替代第5部分 DID/TWFE 主结论。

## 运行说明
本轮未出现需要用户介入的硬性环境问题。估计过程中仅对 sklearn 旧版本不支持 `mean_squared_error(..., squared=False)` 的兼容问题做了内部修正，已自行解决。


## 2026-04-12 v3补充：DML定位
- DML属于高维稳健性补充，用于降低高维干扰项下的模型误设风险。
- DML结果不能替代 DID/TWFE 主识别，只能作为方向一致或信号增强的补充证据。
