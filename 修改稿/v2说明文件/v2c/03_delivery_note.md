# v2c Delivery Note

## 本轮修改了什么

- 将全文主线从“较强影响/优化叙事”收口为“`treat_share` TWFE 下的条件关联 + 推进结构重组 + 边界诊断”。
- 重写了副标题、摘要、引言方法段与结果段、H1/H2、4.3 处理变量说明、5.2 基准结果段、5.4 机制边界段、6 结论关键段。
- 新增了两组补充材料：
  - 附录A：`treat_share` 定义、province-year 重构表、处理时点表、删样清单
  - 附录B：log-ratio fresh re-estimate 结果与说明
- 输出了对象保留版 `docx`，并保留原表格/图形对象。

## 哪些建议被采纳

- 采纳：全文识别语言降格为条件关联证据
- 采纳：H1/H2 收口为相对份额重组与阶段性关联
- 采纳：`treat_share` 公式化、样本流转写实、province-year 层复核资产落地
- 采纳：将 log-ratio 作为构成性补强写入主文与附录
- 采纳：机制结果继续降格为“接口优先、治理重心重分布”
- 采纳：维持 ML、wild bootstrap、stack DID、cohort ATT、IV 等为边界或扩展层

## 哪些建议未直接采纳

- 未直接采纳：group-time ATT / interaction-weighted event study
  - 原因：当前仓库未落地外部可核验处理起点，不满足硬做新主识别的前提。
- 未直接采纳：完整 compositional / fractional 主模型体系
  - 原因：正式结果层没有对应主结果，本轮只做最近可行的 log-ratio 补强。
- 未直接采纳：将 `ppp_quality_zindex` 抬升为主结论
  - 原因：与正式结果边界冲突。
- 未直接采纳：将项目级 ML 或 8.5 IV 抬升为主证明
  - 原因：与正式状态表和论文主线冲突。

## 是否重跑数据 / 回归 / 作图

- 回归：是
  - 在正式 V3 主面板 `262` 个观测上 fresh re-estimate 了执行/采购对数比率规格。
- 作图：否
  - 没有新增图形对象；沿用对象保留稿中的既有图表对象。
- 表格：是
  - 新增附录A/B 的 CSV/Markdown 复核资产。

## 修改后文件清单

- 正文 `md`：
  - `PPP论文_完整论文初稿_公共管理风格_顶刊冲刺整合稿_v2c_本轮修订版_20260418.md`
- 对象保留 `docx`：
  - `PPP论文_完整论文初稿_公共管理风格_顶刊冲刺整合稿_v2c_本轮修订版_20260418_对象保留版.docx`
- 说明文件：
  - `MISSING_INPUTS.md`
  - `00_input_mapping.md`
  - `01_revision_tasklist.md`
  - `02_verification_report.md`
  - `03_delivery_note.md`
- 补充资产：
  - `appendix_A_*`
  - `appendix_B_*`
  - `generate_v2c_object_preserving_docx_20260418.py`
  - `docx_generation_log_20260418.md`
  - `sanitize_v2c_docx_forbidden_phrase_20260418.py`
  - `docx_sanitization_log_20260418.md`

## 风险点与后续建议

- 最高优先级待补项：城市级处理名单、处理阈值与原始 `08_GovService_DID` 底表的显式落地。
- 若后续要继续冲击更高等级投稿，建议在不改变主线的前提下，把城市级处理清单独立整理成匿名可复核附录，再决定是否补更强识别。
- 本轮交付已经把“最近可行版本”做到了正式口径一致，但它仍然受制于原始 `v2c` 正文缺失这一前置条件。
- 对象保留 `docx` 在最终交付前已做一次只改 `document.xml` 文本的净化，用于清除旧替换链条残留的禁用短语；该操作不重绘图表、不改对象数量。
