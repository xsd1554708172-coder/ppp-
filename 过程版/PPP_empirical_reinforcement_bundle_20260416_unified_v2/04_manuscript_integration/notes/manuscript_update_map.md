# Manuscript update map

Target manuscript inspected: `PPP论文_完整论文初稿_公共管理风格_修订版_定点替换_20260415.docx`

## Paragraph-level replacements

1. Replace the entire current section **5.6 稳健性检验** with:
   - `text/section_5_6_replacement.md`

2. If a transition sentence is needed at the end of section 5.3, add:
   - “基于上述识别边界，后文不再简单堆叠替代方法，而是围绕共同趋势设定、样本驱动风险和小样本推断偏乐观等关键脆弱点，依次实施主识别防守型稳健性检验。”

3. If abstract and conclusion need one extra sentence each, use:
   - `text/abstract_and_conclusion_additions.md`

## Table / figure replacements

1. Keep table 4 unchanged as the main identification anchor.
2. Update the robustness summary table in section 5.6 with:
   - `tables/robustness_defense_summary.xlsx`
3. Use the following figures for section 5.6:
   - `01_trend_adjusted_DID/figures/Figure_8A_baseline_vs_trend_adjusted_forest.png`
   - `02_leave_one_province_out_jackknife/figures/Figure_8B_leave_one_province_out_stability.png`
4. Do **not** elevate stack DID, cohort ATT, or supplementary dynamic diagnostics to the same level as the two figures above.

## Caption / note replacements

Use:
- `notes/table_figure_caption_notes.md`

This file contains the recommended caption language and reading boundaries for the updated table and figures.
