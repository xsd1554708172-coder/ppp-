# v1d Verification Report

## Verification Scope

- 工作输出目录：
  - `C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\修改稿\v1说明文件\v1d`
- forward-apply 对象：
  - Markdown base：
    - `C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\修改稿\v1说明文件\v1c\PPP论文_完整论文初稿_公共管理风格_顶刊冲刺整合稿_v1c_codexrev_20260418.md`
  - object-preserving base：
    - `C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\修改稿\v1修改稿留底\v1c\PPP论文_完整论文初稿_公共管理风格_顶刊冲刺整合稿_v1c_codexrev_20260418.docx`

## 1. Reviewed Manuscript Mapping Check

- 结论：`Pass with forward-apply caveat`
- 结果：
  - 两份评审报告点名的 exact reviewed manuscript
    - `01_revised_manuscript_v1c_content_only.docx`
    - `01_revised_manuscript.docx`
    均未在仓库中找到。
  - `v1d` 已明确记录为：
    - `forward-applied revision on the latest extant v1c manuscript representation`

## 2. Official Result Entity Check

### 2.1 Source-of-truth Status Tables

- `PPP_v3结果层状态表_20260413_1345.xlsx` 已核对：
  - `5.3/5.4/8.1-8.5/8.6` 都已基于当前 V3 主面板重估。
  - `8.5` 只定位为 `IV 可行性评估`，不是正式 IV 识别。
- `PPP_变量与模型最终采用口径表_20260413_1345.xlsx` 已核对：
  - 正式主面板、正式文本省年口径、正式文档口径和 5.3/5.4/8.1-8.3/8.4/8.6 结果实体路径均明确。

### 2.2 Baseline 5.3 Coefficients Rechecked

- 文件：
  - `C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\ppp论文数据\01_第3到第8部分_最终修正版\第5部分_核心实证识别\（5.3）基准多期DID_TWFE正式回归\PPP_第5部分_5.3正式回归结果长表_V3_重估版_20260413_1048.csv`
- `treat_share` 对三项主结果的正式估计再次核对为：
  - `exec_share = 0.3556277048`, `se = 0.1001636130`, `p = 0.0003845469`, `N = 262`
  - `proc_share = -0.4022774861`, `se = 0.1019090047`, `p = 0.0000789984`, `N = 262`
  - `ppp_quality_zindex = 0.5252969356`, `se = 0.4213976845`, `p = 0.2125593654`, `N = 262`

### 2.3 Defensive Robustness Summary Rechecked

- 文件：
  - `C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\PPP_empirical_reinforcement_bundle_20260416_unified_v3\04_manuscript_integration\tables\robustness_defense_summary.xlsx`
- 复核结果：
  - `exec_share`
    - baseline `0.3556`
    - trend-adjusted `0.2263`, `p = 0.1945`
    - wild-cluster `p = 0.0761`
    - 结论：`方向稳定但强度减弱`
  - `proc_share`
    - baseline `-0.4023`
    - trend-adjusted `-0.3521`, `p = 0.0485`
    - wild-cluster `p = 0.1221`
    - 结论：`主结论防守性最强`
  - `ppp_quality_zindex`
    - baseline `0.5253`, `p = 0.2126`
    - trend-adjusted `-0.1699`, `p = 0.6780`
    - wild-cluster `p = 0.2372`
    - 结论：`boundary_result_only`

## 3. Sample Flow And Variable Transparency Check

- 正式主面板文件：
  - `C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\ppp论文数据\01_第3到第8部分_最终修正版\第5部分_核心实证识别\（5.1）识别框架、并表与模型设定\PPP_3.6_model_ready_panel_v3_统一口径_方案2_实际执行版_20260413_1048.xlsx`
- 正式文本变量文件：
  - `C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\ppp论文数据\01_第3到第8部分_最终修正版\第4部分_文本变量构造\（4.1-4.4）文本变量构造与输出\PPP_province_year_variables_v3_DID主识别窗口_方案2_平衡口径_实际执行版_20260413_0912.csv`
  - `C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\ppp论文数据\01_第3到第8部分_最终修正版\第4部分_文本变量构造\（4.1-4.4）文本变量构造与输出\PPP_doc_level_variables_v3_DID主识别窗口_2014_2022_地方样本_实际执行版_20260413_0912.csv`
- fresh check：
  - 文档级样本：`1307`
  - 平衡省—年观察：`288`
  - 主面板观察：`266`
  - 正式估计观察：`262`
  - `treat_share` 样本均值：`0.3008`
  - `exec_share` 样本均值：`0.7061`
  - `proc_share` 样本均值：`0.2794`
- 变量工程链条再次核对：
  - `build_ppp_text_variables_v2.py` 展示了 `clean_text -> topic merge -> dictionary phrase counts -> _cnt/_idx -> A/B/C -> 综合指数` 的正式构造链。
  - `README_本部分文件总说明.txt` 与 `README_四级十二类重建说明.md` 支撑“人工框架建模 + 正式词典 + Word2Vec 扩词 + BERTopic 映射 + D 类主要服务机制/扩展分析”的写法。

## 4. Manuscript Text Check

- `title / abstract / introduction / conclusion`：`Pass`
  - 本轮新增透明度说明、变量范围说明、ML 收束和结论压缩已在 `.md` 中落地。
- `main identification remains treat_share DID/TWFE`：`Pass`
- `trend-adjusted DID / leave-one-province-out / wild cluster / stack DID / cohort ATT / DML / IV not elevated to main identification`：`Pass`
- `event study not written as proof of parallel trends`：`Pass`
- `ppp_quality_zindex not elevated`：`Pass`
- `positive V3 / 第9部分 residual wording removed from main text`：`Pass`

## 5. Object-preserving DOCX Check

- 对比文件：
  - source docx：
    - `C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\修改稿\v1修改稿留底\v1c\PPP论文_完整论文初稿_公共管理风格_顶刊冲刺整合稿_v1c_codexrev_20260418.docx`
  - output docx：
    - `C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\修改稿\v1说明文件\v1d\PPP论文_完整论文初稿_公共管理风格_顶刊冲刺整合稿_v1d_codexrev_20260419.docx`
- zip entry 检查：
  - `same_entries = True`
  - `src_entries = 23`
  - `out_entries = 23`
- 关键新增段落抽取检查：
  - 样本流重写段：`Found`
  - 文本变量黑箱性缓解段：`Found`
  - 变量取值范围与均值段：`Found`
  - 收束后的 5.7 段：`Found`
  - 压缩后的学术补位段：`Found`
  - 压缩后的三条政策建议段：`Found`

## 6. Data / Rerun / Workbook Edit Check

- `raw workbook edited`：`No`
- `derived formal results edited`：`No`
- `regression rerun this round`：`No`
- `figure/table regenerated this round`：`No`
- 说明：
  - 本轮未发现必须修正原始数据或重跑模型才能维持 manuscript-facing consistency 的冲突。
  - 因而执行的是“正式资产复核 + 文稿边界与透明度修订”，而不是新的数据生产轮次。

## Verification Conclusion

- `v1d` 已通过本轮 fresh verification，可作为当前最新 v1 manuscript workflow output。

## Remaining Risks

- exact reviewed v1c source 仍然缺失，因此 `v1d` 是 forward-applied revision，而不是对缺失源稿的直接修改。
- 两份评审报告建议中的 `group-time ATT / continuous DID / randomization inference / 独立文本变量效度统计包` 本轮没有 fresh、正式、可审计结果实体，故未落地到正文。
