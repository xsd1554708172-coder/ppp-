# AGENTS.md

## Project mission
This repository supports a PPP paper revision workflow.
Default objective: improve empirical credibility, manuscript consistency, and reproducibility without changing the paper's main research structure.

## Main identification hierarchy
- The ONLY main identification strategy is `treat_share` multi-period DID / TWFE.
- Do NOT silently replace the main model with another estimator.
- `trend-adjusted DID`, `leave-one-province-out`, `stack DID`, `cohort ATT`, `wild bootstrap`, and other supplementary methods are not the main model unless the user explicitly says otherwise.

## Evidence boundaries
- Never write that `event study` establishes parallel trends unless the evidence clearly supports it.
- Never overstate weak or unstable evidence.
- If a result is directionally positive but statistically unstable, keep that limitation explicit.
- Do not turn non-significant results into strong conclusions.
- Do not claim full governance-quality improvement if the stable evidence mainly supports structural improvement.

## Paper storyline guardrails
- Keep the paper's main storyline centered on PPP推进结构改善优先.
- Preserve the distinction between:
  - main identification
  - defensive robustness
  - boundary diagnostics
  - extension analysis
- Do not let text analysis or machine learning dominate the paper's causal argument.

## Text analysis and machine learning role
- Text analysis serves variable construction, mechanism interpretation, and extension analysis.
- Machine learning is extension analysis, not the main identification strategy.
- Do not rewrite the paper into a method-showcase.

## Writing style
- Use a rigorous, restrained, professional, non-hype academic tone.
- Prefer precise claims over ambitious claims.
- Do not use flashy "method stacking" rhetoric.
- Keep manuscript-facing language different from engineering-facing language.

## Data and result discipline
- Use real project files as the only factual basis.
- Do not fabricate coefficients, significance, mechanisms, cases, interviews, or figure content.
- If the current files do not support a suggestion, say so and give the closest feasible alternative.

## Reproducibility and consistency
- Before declaring completion, verify that tables, figures, manuscript replacement text, and README use consistent result values.
- Do not leave multiple manuscript-facing baseline references active at the same time.
- If there is a mismatch between official reported values and fresh reruns, surface it explicitly and keep manuscript-facing outputs consistent.

## Manuscript integration discipline
- When updating the paper, inspect the actual manuscript file and anchor changes to real section/table/figure locations.
- Prefer patch-style replacement files when direct manuscript editing is not performed.
- Keep captions, notes, summary tables, and body text aligned.

## Revision archive and Git sync
- Any new manuscript revision produced under `修改稿` must also be copied into the matching archive folder: `修改稿/v1修改稿留底` for `v1*` versions and `修改稿/v2修改稿留底` for `v2*` versions.
- Archive filenames must stay short and use the pattern `<version-token>_<MMDD_HHMM>.<ext>`, for example `v1a_0419_0012.docx`.
- Prefer one archive subfolder per version token (for example `修改稿/v1修改稿留底/v1a/`).
- After each completed revision task, update the local Git repository and push to the configured GitHub remote if one is available.

## AGENTS.md maintenance rule
- Keep this file concise and durable.
- Add new rules only if they are repeatedly needed, repeatedly violated, likely to recur across many tasks, or materially affect credibility or the paper's main line.
- Put one-off task details in the current prompt or a task-specific markdown file, not here.
