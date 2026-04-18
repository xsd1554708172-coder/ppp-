import matplotlib as mpl
from matplotlib.font_manager import FontProperties

FONT_PATH = r"/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"

def setup_chinese_fonts():
    fp = FontProperties(fname=FONT_PATH)
    mpl.rcParams["font.family"] = fp.get_name()
    mpl.rcParams["axes.unicode_minus"] = False
    mpl.rcParams["pdf.fonttype"] = 42
    mpl.rcParams["ps.fonttype"] = 42
    mpl.rcParams["svg.fonttype"] = "none"
    return FONT_PATH
