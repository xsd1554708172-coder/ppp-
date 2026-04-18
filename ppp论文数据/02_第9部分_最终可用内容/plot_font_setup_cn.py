
import matplotlib.pyplot as plt
from matplotlib import font_manager

def setup_chinese_fonts(preferred=None):
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
    if chosen is not None:
        plt.rcParams["font.sans-serif"] = [chosen]
    else:
        print("WARNING: No Chinese font found. Install one of:", candidates)
    plt.rcParams["axes.unicode_minus"] = False
    return chosen
