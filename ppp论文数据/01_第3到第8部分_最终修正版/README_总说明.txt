PPP论文第3至第8部分完整文件归档（补全Python脚本与中文字体修复）

本归档修正了上一版的两个问题：
1. 补上了缺失的 Python 代码文件（包括原始脚本与新增复现脚本）。
2. 补上了中文字体修复辅助文件：plot_font_setup_cn.py 与 README_中文字体修复说明.py。

使用说明：
- 对所有需要重新出图的本地脚本，在文件顶部加入：
    from plot_font_setup_cn import setup_chinese_fonts
    setup_chinese_fonts()
- 然后在本地重新运行相应绘图脚本，即可修复中文缺字问题。
- 本次修订新增 text_missing / text_observed，用于显式控制“无文本覆盖”单元。
- treat_share / did_any / did_intensity 的精确聚合公式已另行写入《README_版本与口径统一说明_20260412_修订版.txt》与5.1工作簿。
