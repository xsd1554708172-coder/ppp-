# v1e log-ratio 补充估计说明

- 正式样本：`baseline_sample_5_3 == 1`，N = `262`
- 最小正份额：`0.0067114094`
- 基准连续性修正：`c = 0.0033557047`
- 估计框架：与表4相同的 `treat_share + controls + province FE + year FE`，省级聚类，正态近似 `p` 值。
- 作用定位：份额型结果变量的构成性补强，不替代 `treat_share` 多期 DID/TWFE 主识别。