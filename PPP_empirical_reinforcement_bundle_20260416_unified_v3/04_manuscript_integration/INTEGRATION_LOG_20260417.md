# 整合说明

## 底稿来源

本次整合以 `（2026.4.15）已确认采用的图和表\PPP论文完整正文初稿_公共管理风格_20260415.md` 作为正文底稿，同时以 `PPP论文_完整论文初稿_公共管理风格_修订版_定点替换_20260415.docx` 的 `word/document.xml` 为真实章节结构锚点，对摘要、第二章、第三章、第四章、第五章第5.3节与第5.6节、第5.7节以及第六章进行了统一修订。

## 并入的补丁

本次完整并入了两类 manuscript-facing 补丁。

第一类是 DID 补强补丁：
- `04_manuscript_integration\notes\EXACT_REPLACEMENT_PATCH_20260417.md`
- `04_manuscript_integration\section_5_6_final.md`
- `04_manuscript_integration\abstract_final_patch.md`
- `04_manuscript_integration\conclusion_final_patch.md`

第二类是 supplement 补丁：
- `04_manuscript_integration\EXACT_REPLACEMENT_PATCH_SUPPLEMENT_20260417.md`
- `04_manuscript_integration\notes\literature_review_supplement_patch_20260417.md`
- `04_manuscript_integration\notes\theory_supplement_patch_20260417.md`
- `04_manuscript_integration\notes\methods_supplement_patch_20260417.md`
- `04_manuscript_integration\notes\conclusion_and_extension_supplement_patch_20260417.md`
- `04_manuscript_integration\notes\references_cleanup_patch_20260417.md`

## 风格统一动作

本次整合对全文进行了去 patch 化处理，主要包括：

1. 删除了所有施工型占位和编辑说明，如“此处插入”“建议新增”“保留原文”“patch”“replacement”等。
2. 将第五章标题统一为“实证结果与分析”，并将第5.6节按“主识别防守”逻辑重写。
3. 将原有稳健性部分中的工程语言和内部口径说明删除，保留与正文审读直接相关的学术表述。
4. 将图表体系统一为“图8A/图8B + 表8 + 表9”的 manuscript-facing 结构，并将安慰剂图示降为补充材料层面的诊断性图示。
5. 对摘要、引言、结论进行了进一步压缩与升格，使其更接近投稿稿件的学术风格，而非项目说明文本。

## 当前仍待人工核校的参考文献信息

以下条目的作者、年份或期刊信息尚未在当前材料下完成最终 bibliographic 核校，因此在整合稿中采用了克制写法，未补写无法可靠确认的卷期页码：

- 《政策信息学视角下政策文本量化方法研究进展》
- 《基于BERTopic的计算机视觉领域热点技术主题及演化分析》
- 《基于深度学习的我国科技政策属性识别》

此外，A3、A4、B1、B3、B4、B5、C3、C4、A1 等条目虽然已能较可靠识别作者、题名、年份和部分期刊信息，但卷期页码仍建议在投稿前依据原始 PDF 或数据库再做一次人工核校。

## 本次整合的边界

1. 主识别仍然唯一保留为 `treat_share` 多期 DID / TWFE。
2. `trend-adjusted DID`、`leave-one-province-out` 和 `wild cluster bootstrap` 只以主识别防守层或边界说明层进入正文。
3. `stack DID`、`cohort ATT` 和动态补充识别只保留为边界诊断，不写成第二主模型。
4. `ppp_quality_zindex` 继续只作为方向性信号而非稳健主结论。
5. 项目级模型继续限定为治理辅助识别，不参与因果识别叙事。
