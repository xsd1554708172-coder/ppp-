# stackDID规格筛查说明_最终版

- 正式输入主面板：`ppp论文数据\01_第3到第8部分_最终修正版\第5部分_核心实证识别\（5.1）识别框架、并表与模型设定\PPP_3.6_model_ready_panel_v3_统一口径_方案2_实际执行版_20260413_1048.csv`
- 基准DID结果表：`ppp论文数据\01_第3到第8部分_最终修正版\第5部分_核心实证识别\（5.3）基准多期DID_TWFE正式回归\PPP_第5部分_5.3正式回归结果长表_V3_重估版_20260413_1048.csv`
- 本轮筛查维度：控制组定义（never only / never+not-yet）、事件窗口（[-2,+2] / [-3,+2] / [-2,+1]）。

## 已测试规格
- `stack_never_w2`：Stack DID：never-treated only，窗口[-2,+2]
- `stack_later_w2`：Stack DID：never+not-yet-treated，窗口[-2,+2]
- `stack_never_w3_2`：Stack DID：never-treated only，窗口[-3,+2]
- `stack_later_w3_2`：Stack DID：never+not-yet-treated，窗口[-3,+2]
- `stack_never_w2_1`：Stack DID：never-treated only，窗口[-2,+1]
- `stack_later_w2_1`：Stack DID：never+not-yet-treated，窗口[-2,+1]

## 筛查结论
- `never-treated only` 与 `never+not-yet-treated` 的点估计几乎相同，说明控制组定义不是当前结果波动的主要来源。
- `[-3,+2]` 相比 `[-2,+2]` 只增加极少观测，却未改善统计强度，反而增加了处理前噪声暴露。
- `[-2,+1]` 样本更小，执行阶段与采购阶段的统计支持整体更弱，因此不宜作为主规格。
- 最终采用 `stack_never_w2` 作为Stack DID主规格：它在合法规格中保持了最清晰的方向判断和最可读的样本结构，但仍只能支撑“方向一致、统计强度减弱”的补充识别表述。