
"""
This file is a local-use note for fixing Chinese font rendering in plots.

1. Put `plot_font_setup_cn.py` in the same folder.
2. At the top of any plotting script, add:

    from plot_font_setup_cn import setup_chinese_fonts
    setup_chinese_fonts()

3. Re-run the plotting script locally.

This solves the common issue where Chinese characters appear as squares or missing glyphs.
"""
