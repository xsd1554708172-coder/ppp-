# v1c Revision Tasklist

## Input Status

- token-local 正文稿件本体：`缺失`
- token-local 修改建议文件：`已匹配`
- official fallback base：`已使用`

## Extracted Tasks And Execution

### 1. 纯文字修订

- `已执行` 将标题从 `政务服务数字化改革如何重塑PPP项目推进结构？` 调整为 `政务服务数字化改革与PPP项目推进结构调整`，降低无新增识别补强情况下的过强承诺。
- `已执行` 将摘要压缩到 `344` 字符，删除方法堆叠，保留 `treat_share`、`exec_share`、`proc_share`、`ppp_quality_zindex` 与主识别边界。
- `已执行` 统一 manuscript-facing 语言，避免将 `ppp_quality_zindex`、事件研究和项目级模型写成主结论。

### 2. 理论/机制修订

- `已执行` 将 H2 改写为“程序环境调整推动采购向执行转换”，弱化与 H1 的主效应重叠。
- `已核查未重写` 第 2 章四组文献结构在 `20260418` official base 中已基本落地，本轮未新增未核验参考文献。

### 3. 识别策略与结果边界修订

- `已执行` 在第 5.3 节动态路径段补入对前趋势可能来源的解释，并继续把事件研究限定为“动态路径与识别边界诊断”。
- `已执行` 在第 5.6.4 节把 `PSM-DID`、`DML`、`IV` 解释为“敏感性暴露/边界诊断”，不再留下额外背书空间。
- `已执行` 保持唯一主识别为 `treat_share` 多期 DID / TWFE，没有抬升其他方法为主模型。

### 4. 表图与附录口径

- `已核查未重作图` `table_figure_caption_notes.md` 已与正文第 5.6 节防守型稳健性口径一致，本轮未重生成图表。
- `已核查未重表` 本轮没有改写表 4、表 8、图 8A、图 8B、图 9 的数值层内容，只修订其正文解释口径。

### 5. 政策建议修订

- `已执行` 将第 6 章政策含义改写为按主体分工的版本：
  - 政务服务管理部门
  - 发展改革部门
  - 财政与行业主管部门
  - 审计/监管/项目管理部门

### 6. 数据/结果口径核对

- `已核对` 基准 DID 正式结果实体：
  - `exec_share` × `treat_share` = `0.3556277048`
  - `proc_share` × `treat_share` = `-0.4022774861`
  - `ppp_quality_zindex` × `treat_share` = `0.5252969356`，`p = 0.2126`
- `已核对` PSM-DID 敏感性结果实体：
  - `exec_share` × `treat_share` = `-0.5360932308`，`p = 0.0871`
  - `proc_share` × `treat_share` = `0.3104223083`，`p = 0.3739`
  - `ppp_quality_zindex` × `treat_share` = `-2.6388945174`，`p < 0.001`
- `未重跑` 本轮没有重估回归或重作图，因为当前正式结果资产已存在，且本轮主要处理 review-driven manuscript revision。

## Not Adopted This Round And Reasons

- `组—时 ATT / 连续处理 DID / 随机化推断重跑`
  - `未采纳`
  - 原因：当前正式 authority hierarchy 仍明确 `treat_share` 多期 DID / TWFE 为唯一主识别；本轮也没有产出新的、经过正式审计的替代结果实体。

- `文本变量外部效度附录（人工编码一致性、替代词典、主题稳定性）`
  - `未采纳`
  - 原因：当前项目文件未提供 fresh、可审计的新增结果输出；编造附录或补造一致性指标被禁止。

- `新增表图或附录重生成`
  - `未采纳`
  - 原因：当前正式 caption/notes 已可支撑本轮边界修订；本轮 substantive change 集中在正文口径与解释层。

- `直接恢复 token-local v1c 正文稿`
  - `无法执行`
  - 原因：`01_revised_manuscript_v1c_content_only.docx` 缺失，且在 workspace-wide filename scan 中未找到。
