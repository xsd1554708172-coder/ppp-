
import os
import platform
import matplotlib.pyplot as plt
from matplotlib import font_manager

def setup_chinese_fonts(preferred=None):
    """
    Configure matplotlib to display Chinese on Windows/macOS/Linux.
    Usage:
        from plot_font_setup_cn import setup_chinese_fonts
        setup_chinese_fonts()
    """
    candidates = preferred or [
        "Microsoft YaHei", "SimHei", "SimSun", "Noto Sans CJK SC",
        "PingFang SC", "Heiti SC", "Arial Unicode MS", "WenQuanYi Zen Hei"
    ]
    available = {f.name for f in font_manager.fontManager.ttflist}
    chosen = None
    for c in candidates:
        if c in available:
            chosen = c
            break
    if chosen is None:
        print("WARNING: No common Chinese font found. Please install one of:", candidates)
    else:
        plt.rcParams["font.sans-serif"] = [chosen]
    plt.rcParams["axes.unicode_minus"] = False
    return chosen
