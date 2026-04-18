# Manuscript anchor inspection

Inspected target manuscript:

- `PPP论文_完整论文初稿_公共管理风格_修订版_定点替换_20260415.docx`

## Relevant anchors confirmed

- Section headings present in the document XML:
  - `5.3 动态路径与识别边界`
  - `5.6 稳健性检验`
  - `5.7 项目级扩展分析：高低风险的辅助识别`
- The current 5.6 block already mixes several robustness numbers, but it does not yet clearly separate:
  - trend-adjusted DID as the main defense layer,
  - leave-one-province-out as the sample-driven diagnostic,
  - small-sample inference as appendix-level support,
  - stack DID / cohort ATT as downgraded boundary diagnostics.

## Implication for replacement

The manuscript does not need a new empirical chapter. It needs a structured replacement of section 5.6 plus synchronized caption, note, and paragraph updates. That is why this bundle provides:

- `text/section_5_6_replacement.md`
- `notes/table_figure_caption_notes.md`
- `notes/manuscript_update_map.md`

These files should be treated as the exact integration layer between the rerun outputs and the current `.docx`.
