# Unified Baseline Reference

## Canonical rule
- The only canonical main identification in this bundle is `treat_share` DID/TWFE.
- `did_any` and `did_intensity` remain comparison specifications only.
- `trend-adjusted DID` is a defensive robustness layer and does not replace the canonical baseline.

## Source chain
- 正文锚点：`PPP论文_完整论文初稿_公共管理风格_修订版_定点替换_20260415.docx`
- 正式 V3 主面板：`ppp论文数据/01_第3到第8部分_最终修正版/第5部分_核心实证识别/（5.1）识别框架、并表与模型设定/PPP_3.6_model_ready_panel_v3_统一口径_方案2_实际执行版_20260413_1048.csv`
- 5.3 正式回归长表：`ppp论文数据/01_第3到第8部分_最终修正版/第5部分_核心实证识别/（5.3）基准多期DID_TWFE正式回归/PPP_第5部分_5.3正式回归结果长表_V3_重估版_20260413_1048.csv`

## Why 1048 is canonical
- The 20260413_1048 and 20260413_0912 panel files are byte-for-byte identical in row content and columns.
- The 1048 file is the final timestamped file used by the current 5.3 long table, so it is the cleanest canonical reference for downstream modules.

## What this workbook records
- The exact正文 anchor paragraphs that define the baseline DID framing.
- The 5.3 baseline coefficients for `exec_share`, `proc_share`, and `ppp_quality_zindex`.
- A relative-path index so every downstream module can stay path-relative.

## Baseline numbers
- `exec_share`: 0.355628, p=0.000385
- `proc_share`: -0.402277, p=0.000079
- `ppp_quality_zindex`: 0.525297, p=0.212559
