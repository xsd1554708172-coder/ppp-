PPP Part 8 Robustness Bundle

Contents
- charts/: 11 robustness figures (PNG, PDF, SVG)
- input_data/: actual input spreadsheets used for figure generation
- code/generate_part8_full11.py: relative-path reproduction script
- requirements.txt: Python dependencies
- input_file_mapping_utf8bom.csv: bundle file ↔ original source file mapping
- generation_info.json: generation notes
- preview_contact_sheet.png: preview sheet

Design logic
Section 8 is rebuilt around four evidence blocks:
1) Conventional robustness checks (alternative outcomes / treatments, lagged controls, sample restrictions)
2) Matched-sample DID / PSM-DID diagnostics
3) IV feasibility screening rather than forced IV estimation
4) DML as a high-dimensional robustness direction

How to reproduce
1. Unzip bundle
2. pip install -r requirements.txt
3. python code/generate_part8_full11.py
Outputs will be written to charts_regenerated/
