# v1c Missing Inputs

## Missing Item

- `v1c` token-local 正文稿件本体

## Expected Vs Actual

### Expected

- 应位于：
  - `C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\修改稿\v1`
- 理想状态下，应存在与 `v1c` 对应的正文底稿，供逐段修订与对象回填。

### Actual

- 实际扫描结果只发现：
  - `C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\修改稿\v1\v1c_top_journal_review_report.docx`
- 该文件经内容判定属于：
  - `复审/修改报告`
  - 不是正文稿件本体
- 报告中被审查的正文目标为：
  - `v1c.zip / 01_revised_manuscript_v1c_content_only.docx`
- 该被审查正文文件未在当前 workspace 中找到。

## Not Missing This Round

- `C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\修改稿\v1修改建议\v1c_top_journal_review_report.docx`
  - 已存在
  - 属于 exact-token 建议文件

## Paths Checked

- `C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\修改稿\v1`
- `C:\Users\陈楚玲\Desktop\ppp论文数据\codex项目\修改稿\v1修改建议`
- workspace-wide filename scan：
  - `v1c`
  - `01_revised_manuscript_v1c`
  - `content_only`

## What This Still Blocks

- 无法证明本轮新稿与缺失的 token-local `v1c` 正文是一一对应的直接修订关系。
- 无法判断 `20260418 official base` 与缺失的 `01_revised_manuscript_v1c_content_only.docx` 是否完全一致。

## Mitigation Used This Round

- 采用用户指定的 `20260418` 正式整合稿与对象保留投稿版作为 fallback 正文底稿。
- 保持正式结果表与变量口径表为上位依据。
- 在 `00_input_mapping.md` 中明确记录 fallback 决策与 residual risk。

## Residual Risk

- 若缺失的 token-local 正文与 `20260418 official base` 存在未观察差异，本轮修订无法覆盖那部分差异。
- 因而，本轮输出应被理解为：
  - `v1c official-base fallback revision`
  - 而不是 `direct recovery of missing token-local manuscript`
