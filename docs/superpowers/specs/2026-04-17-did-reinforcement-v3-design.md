# DID Reinforcement v3 Design

## Scope

This revision does not change the paper's main identification strategy. The only main model remains `treat_share` multi-period DID / TWFE. The purpose of this round is to turn the existing reinforcement bundle into a final manuscript-ready package with one manuscript-facing baseline anchor, one reproducible engineering path, and one coherent manuscript patch layer.

## Design decisions

1. **Single manuscript-facing baseline**
   - All reinforcement modules must compare against one canonical baseline DID reference.
   - Any archived-vs-rerun comparison is allowed only as engineering validation, not as a second manuscript-facing baseline.

2. **Defense-layer hierarchy**
   - Main text defense layer: `trend-adjusted DID`
   - Main text auxiliary diagnostic: `leave-one-province-out / jackknife`
   - Appendix / short-paragraph boundary layer: `wild bootstrap / small-sample inference`
   - `stack DID`, `cohort ATT`, and dynamic supplementary identification remain downgraded boundary diagnostics.

3. **Manuscript integration strategy**
   - Do not rewrite the paper.
   - Replace section 5.6 with a structured defense-oriented version.
   - Keep Table 4 as the unchanged main identification anchor.
   - Update captions, notes, abstract supplement, conclusion supplement, and patch instructions so they all point to the same hierarchy.

4. **Packaging rule**
   - The final output should be a clean bundle named `PPP_empirical_reinforcement_bundle_20260416_unified_v3`.
   - The bundle must either be self-contained or state its input prerequisites unambiguously.

## Execution tracks

- **Track A:** baseline unification + trend-adjusted DID
- **Track B:** leave-one-province-out + small-sample inference downgrade + figure split into manuscript/diagnostic versions
- **Track C:** manuscript `.docx` anchoring + section 5.6 patch + captions/notes + final patch files

## Non-goals

- No new main estimator
- No stronger prose than the evidence supports
- No event-study claim of established parallel trends
- No elevation of `ppp_quality_zindex` to a headline conclusion without stable support
