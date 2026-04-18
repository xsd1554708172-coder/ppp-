# 第6部分 6.6 严格中介效应分解（V2 四级十二类）

## 本轮完成内容
- 中介变量：`A_idx`
- 处理变量：`treat_share`
- 结果变量：`exec_share`、`proc_share`、`ppp_quality_zindex`
- 样本量：262
- 固定效应：province FE + year FE
- 聚类：province
- Bootstrap：province-level cluster bootstrap，1000 次

## 关键结果
- `exec_share`：间接效应 0.0415，Sobel p=0.3645，95% Bootstrap CI [-0.2792, 0.1634]
- `proc_share`：间接效应 -0.0391，Sobel p=0.3769，95% Bootstrap CI [-0.1573, 0.2645]
- `ppp_quality_zindex`：间接效应 0.0406，Sobel p=0.5125，95% Bootstrap CI [-0.4158, 0.2012]

## 当前可写结论
当前严格中介分解不支持 `A_idx` 对三项结果变量存在稳定显著的单一路径中介效应。更稳妥的表述是：
> 改革首先显著改变治理接口文本结构，但 `A_idx` 单独作为严格中介时，其间接效应并未稳定显著，因此第6.6更支持“部分机制、接口先行”，而不支持强中介已成立。

## 说明
这轮没有停在环境问题上，已直接完成 Sobel 与 Bootstrap 两套结果计算并落盘。
