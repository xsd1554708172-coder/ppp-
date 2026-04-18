
PPP Part 7 Heterogeneity Analysis — Design + Charts Bundle

Contents
- input_data/: source files used for chart generation
- charts/: generated figures (PNG, PDF, SVG)
- code/generate_part7_full11.py: reproducible chart script
- requirements.txt: minimal Python dependencies
- input_file_mapping_utf8bom.csv: filename mapping
- generation_info.json: generation metadata
- preview_contact_sheet.png: visual overview

Design logic
This bundle reorganizes Section 7 around heterogeneity-specific visual tasks rather than repeating forest plots:
1) subgroup contrast
2) interaction significance
3) effect frontier
4) gap ranking
5) risk proxy construction
6) risk exposure subgroup contrast
7) risk exposure decomposition
8) government-data-openness proxy structure
9) openness subgroup contrast
10) overall heterogeneity scorecard
11) heterogeneity flow summary

How to reproduce
1. Install dependencies:
   pip install -r requirements.txt
2. Run:
   python code/generate_part7_full11.py

Notes
- File names are ASCII to avoid zip encoding issues.
- Charts use English labels to avoid font-missing problems across environments.
