# 第4部分文本变量构造结果（V2 四级十二类）

- 文档级变量表：1472 行
- 省—年面板变量表：251 行
- 年份汇总变量表：13 行
- 一级主题：A/B/C/D
- 二级主题：12 个
- 机器主题：24 个

## 关键口径
- 计数变量 `_cnt`：基于新版正式词典V2在真实政策文本中的短语命中次数。
- 强度变量 `_idx`：`cnt / char_len * 10000`。
- 综合指数：`ppp_governance_capacity_index = mean(z_A_idx, z_B_idx, z_C_idx)`；`ppp_norm_risk_index = mean(z_B_idx, z_C_idx, z_D_idx)`。
- `share` 变量：来源于 BERTopic 文档级主题分配的组内均值。

## 注意
- 当前自动主题映射主要集中在 A/B/C，D 类尚未自然形成稳定独立机器主题簇，因此 D 类 share 变量多为 0；但 D 类 cnt/idx 已可直接用于机制和扩展分析。
- 下一步建议直接基于本版变量表重建 model_ready_panel，并重跑 5.2/5.3/5.4 以及第6—8部分。
