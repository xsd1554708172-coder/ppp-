# v2c Verification Report

## 核查时间

- 2026-04-18（本地工作区 fresh verification）

## 核查范围

- 修订后 Markdown 稿件
- 修订后对象保留版 DOCX
- `appendix_A_*` 与 `appendix_B_*` 补充资产
- `generate_v2c_object_preserving_docx_20260418.py` 与 `docx_generation_log_20260418.md`

## 核查结果

### 1. 标题、摘要、引言、结论

- 已将副标题统一为“条件关联证据”口径。
- 摘要已补入 log-ratio 构成性补强，并把主结果界定为“过程性、方向性的条件关联证据”。
- 引言的方法段与结果段已从“直接识别改革影响”收口为“地区和年份固定效应框架下的平均条件关联”。
- 结论第一点已改写为“相对份额重组”，不再把结果写成全面质量提升。

### 2. 主识别与红线

- 全文唯一主识别仍为 `treat_share` 多期 DID/TWFE。
- 未将 `did_any`、`did_intensity`、trend-adjusted DID、wild bootstrap、stack DID、cohort ATT、PSM-DID、DML、IV 候选或项目级 ML 抬升为主识别。
- 事件研究仍定位为“动态路径与识别边界说明”，未出现“平行趋势成立”的写法。
- `ppp_quality_zindex` 继续定位为辅助结果，未被抬高为主结论。

### 3. 数据与结果同步

- 4.3 已同步写入：
  - `treat_share_{pt} = treated_city_count_{pt} / city_n = (1/N_{pt}) × Σ_i treat_i`
  - `post_t = 1[t>=2016]`
  - `did_intensity_{pt} = post_t × treat_share_{pt}`
  - `did_any_{pt} = 1(did_intensity_{pt} > 0)`
- 样本流转已同步写入：
  - V3 主面板 `266` 个省—年观察值
  - 正式估计样本 `262`
  - 排除 `4` 个新疆生产建设兵团观测，原因是基准控制变量不完整
- fresh re-estimate 的 log-ratio 结果已同步到 `md` / `docx` / 附录B：
  - 系数 `3.1916`
  - 标准误 `1.4500`
  - 正态近似 `p = 0.0277`

### 4. 附录与复核资产

- 已生成 `appendix_A_treat_share_reconstruction_20260418.csv`
- 已生成 `appendix_A_province_treatment_timing_20260418.csv`
- 已生成 `appendix_A_sample_exclusions_20260418.csv`
- 已生成 `appendix_A_treat_share_definition_tables_20260418.md`
- 已生成 `appendix_B_log_ratio_reestimate_20260418.csv`
- 已生成 `appendix_B_log_ratio_note_20260418.md`

### 5. 对象保留版核查

- 对象保留版 `docx` 已成功生成。
- `docx_generation_log_20260418.md` 记录：
  - 顶层表格对象数：`13`
  - 顶层图形段落对象数：`12`
  - 仅替换正文段落，不重绘图表对象

## 仍存限制

- 当前仓库没有显式落地城市级处理名单与原始阈值底表，因此附录A只能提供 province-year 层面的重构复核，不能宣称已经完成城市级全量复现。
- 指定 `v2` 目录中没有 `v2c` 原始正文稿件，`v2修改建议` 目录也为空；本轮修订基于 token-local 审查报告与正式整合稿的 fallback 路径完成。

## 结论

- 在现有仓库输入条件下，`v2c` 已完成可交付的实质性修订、正式口径对齐、fresh result 同步与对象保留回填。
- 需要人工进一步补足的唯一高优先级缺口，是城市级处理名单/阈值底表的独立落地。

## 补充核验更新（2026-04-18 夜）

- 在对象保留版生成完成后，又执行了 `sanitize_v2c_docx_forbidden_phrase_20260418.py`，仅对 `word/document.xml` 中残留的旧短语做原位文本替换，不改变对象结构。
- `docx_sanitization_log_20260418.md` 已记录替换次数与新旧 SHA256。
- 末次 fresh verification 显示：`md` 与 `docx` 均包含“条件关联证据”“附录A”“附录B”“3.1916”“266个省—年观察值”，且均不再包含“平行趋势已经成立”。
