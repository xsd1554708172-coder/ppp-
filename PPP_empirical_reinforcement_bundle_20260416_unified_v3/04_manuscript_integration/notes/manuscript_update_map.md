# Manuscript update map

## Manuscript anchor

- File:
  - `PPP论文_完整论文初稿_公共管理风格_修订版_定点替换_20260415.docx`
- Inspection status:
  - actual `.docx` inspected via `word/document.xml`
  - abstract, 5.3 ending, 5.6 block, conclusion, Table 8, Figure 8, and Figure 9 anchors identified from real paragraph text

## Required updates

1. 摘要
   - 在摘要主结果段末尾新增 `abstract_final_patch.md` 中的一句话
   - 锚点句：以“而非即时、全面地提升所有治理质量指标。”收束的摘要段

2. 第5章 5.3 结尾
   - 在事件研究小节最后一句后新增一条承接句
   - 锚点句：以“而不作为强因果识别的附加背书。”收束的段落

3. 第5章 5.6
   - 用 `section_5_6_final.md` 整段替换现有 5.6 全节
   - 真实替换范围：从标题“5.6 稳健性检验”开始，到图9解释句结束，5.7 不在替换范围内

4. 表8
   - 用 `robustness_defense_summary.xlsx` 作为 manuscript-facing summary table
   - 表题与表注按 `table_figure_caption_notes.md` 更新

5. 图8
   - 将单一“图8 主结果稳健性证据阶梯图”改为 Figure 8A 与 Figure 8B 双图结构
   - 使用 bundle 中的正式论文版图片：
     - `01_trend_adjusted_DID/figures/Figure_8A_trend_adjusted_did_20260417_1537.png`
     - `02_leave_one_province_out_jackknife/figures/Figure_8B_jackknife_stability_20260417_1537.png`

6. 图9
   - 图9安慰剂分布图降为附录或补充材料中的诊断图示
   - 若正文仍保留，仅保留一句补充性提及，不再作为5.6主图展开

7. 结论
   - 在结论“稳健性与边界”相关段落新增 `conclusion_final_patch.md` 中的一句话

## Integration boundary

- Main identification remains Table 4 (`treat_share` DID/TWFE)
- Figure 8A and Figure 8B are defensive robustness layers
- wild cluster bootstrap remains boundary support only
- stack DID / cohort ATT / dynamic supplementary identification remain downgraded diagnostics
