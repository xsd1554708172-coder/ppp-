# Small-sample inference notes

This module is a conservative inference check, not a stronger identification strategy.

## Current run summary

- `exec_share`: wild bootstrap p = 0.076; cluster p = 0.00123; direction same as baseline = True.
- `proc_share`: wild bootstrap p = 0.122; cluster p = 0.00041; direction same as baseline = True.
- `ppp_quality_zindex`: wild bootstrap p = 0.237; cluster p = 0.256; direction same as baseline = True.

## Interpretation

The bootstrap result should be written as a cautionary small-sample check. It can support direction consistency, but it should not be used to claim that all estimates remain decisively significant under province-cluster wild bootstrap inference.
