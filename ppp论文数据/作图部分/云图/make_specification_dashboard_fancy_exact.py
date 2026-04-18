import io, zipfile
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.font_manager import FontProperties

FONT_PATH = r"/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
fp = FontProperties(fname=FONT_PATH)
fp_bold = FontProperties(fname=FONT_PATH, weight="bold")

mpl.rcParams["font.family"] = fp.get_name()
mpl.rcParams["axes.unicode_minus"] = False
mpl.rcParams["pdf.fonttype"] = 42
mpl.rcParams["ps.fonttype"] = 42
mpl.rcParams["svg.fonttype"] = "none"
mpl.rcParams["figure.dpi"] = 180
mpl.rcParams["savefig.dpi"] = 240

zip_path = "论文第3至9部分.zip"
zf = zipfile.ZipFile(zip_path)

def try_decode(s):
    for enc in ["gbk", "utf-8", "gb18030", "big5"]:
        try:
            return s.encode("cp437").decode(enc)
        except Exception:
            pass
    return s

name_map = {try_decode(n): n for n in zf.namelist()}

def read_excel_from_zip(dec_name, sheet_name=0):
    raw = zf.read(name_map[dec_name])
    return pd.read_excel(io.BytesIO(raw), sheet_name=sheet_name, engine="openpyxl")

baseline = read_excel_from_zip(
    "第5部分_核心实证识别/（5.3）基准多期DID_TWFE正式回归/PPP_第5部分_5.3基准多期DID正式回归_V2_四级十二类_实际执行版.xlsx",
    "正式回归结果长表"
)
robust_all = read_excel_from_zip(
    "第8部分_稳健性检验/（8.1-8.3）常规稳健性/PPP_第8部分_8.1-8.3常规稳健性_V2_四级十二类_实际执行版.xlsx",
    "全部稳健性结果"
)

base = baseline.copy()
base["source"] = "基准回归"
base["spec"] = "Baseline"
base = base[["source","spec","depvar","did_var","coef","se","p","N"]]

rob = robust_all.copy()
rob["source"] = "稳健性"
rob = rob[["source","spec","depvar","did_var","coef","se","p","N"]]

spec = pd.concat([base, rob], ignore_index=True)
spec = spec[spec["did_var"].isin(["treat_share","did_any","did_intensity"])].copy()
spec = spec[spec["depvar"].isin(["ppp_quality_pca_rebuilt","ppp_quality_zindex","exec_share","proc_share","prep_share"])].copy()
spec["ci_low"] = spec["coef"] - 1.96 * spec["se"]
spec["ci_high"] = spec["coef"] + 1.96 * spec["se"]
spec["sig"] = spec["p"] < 0.05
spec["sig10"] = spec["p"] < 0.10
spec["abs_coef"] = spec["coef"].abs()
spec = spec.sort_values(["coef","depvar","did_var"]).reset_index(drop=True)
spec["x"] = np.arange(len(spec))

dep_order = ["ppp_quality_pca_rebuilt","ppp_quality_zindex","exec_share","proc_share","prep_share"]
did_order = ["treat_share","did_any","did_intensity"]
source_order = ["基准回归","稳健性"]

summary_dep = spec.groupby("depvar").agg(
    total_specs=("coef","size"),
    mean_coef=("coef","mean"),
    median_coef=("coef","median"),
    pos_sig=("coef", lambda s: ((s > 0) & spec.loc[s.index, "sig"]).sum()),
    neg_sig=("coef", lambda s: ((s < 0) & spec.loc[s.index, "sig"]).sum()),
).reindex(dep_order)

summary_did = spec.groupby("did_var").agg(
    total_specs=("coef","size"),
    mean_abs_coef=("abs_coef","mean"),
    sig_rate=("sig","mean"),
).reindex(did_order)

fig = plt.figure(figsize=(18, 13))
gs = fig.add_gridspec(3, 3, height_ratios=[3.3, 1.7, 1.9], width_ratios=[3.6, 1.4, 1.4], hspace=0.22, wspace=0.18)

axA = fig.add_subplot(gs[0, 0])
marker_map = {"treat_share":"o", "did_any":"s", "did_intensity":"^"}
for dep in dep_order:
    d = spec[spec["depvar"] == dep]
    axA.vlines(d["x"], d["ci_low"], d["ci_high"], linewidth=0.8, alpha=0.60)
    for _, r in d.iterrows():
        size = 64 if r["sig"] else (42 if r["sig10"] else 24)
        alpha = 0.95 if r["sig"] else (0.70 if r["sig10"] else 0.35)
        axA.scatter(r["x"], r["coef"], marker=marker_map.get(r["did_var"], "o"), s=size, alpha=alpha)
axA.axhline(0, linewidth=1)
axA.set_title("A. 全部规格的系数—区间云图", loc="left", fontproperties=fp_bold, fontsize=13)
axA.set_ylabel("系数与95%区间", fontproperties=fp)
axA.tick_params(axis="x", labelbottom=False)
for t in axA.get_yticklabels():
    t.set_fontproperties(fp)

axB = fig.add_subplot(gs[0, 1], sharex=axA)
window = max(5, len(spec)//8)
roll = pd.DataFrame({"x": spec["x"], "coef": spec["coef"], "sig": spec["sig"].astype(int), "sig10": spec["sig10"].astype(int)})
roll["roll_mean"] = roll["coef"].rolling(window=window, center=True, min_periods=1).mean()
roll["roll_sig"] = roll["sig"].rolling(window=window, center=True, min_periods=1).mean()
roll["roll_sig10"] = roll["sig10"].rolling(window=window, center=True, min_periods=1).mean()
axB.plot(roll["x"], roll["roll_mean"], linewidth=2)
axB.axhline(0, linewidth=1)
axB.set_title("B. 局部趋势", loc="left", fontproperties=fp_bold, fontsize=13)
axB.set_ylabel("滚动平均系数", fontproperties=fp)
axB.tick_params(axis="x", labelbottom=False)
for t in axB.get_yticklabels():
    t.set_fontproperties(fp)
axB2 = axB.twinx()
axB2.plot(roll["x"], roll["roll_sig10"], linewidth=1.2, linestyle="--")
axB2.plot(roll["x"], roll["roll_sig"], linewidth=1.8, linestyle=":")
axB2.set_ylabel("显著比例", fontproperties=fp)
for t in axB2.get_yticklabels():
    t.set_fontproperties(fp)

axC = fig.add_subplot(gs[0, 2])
ypos = np.arange(len(summary_did))
axC.barh(ypos - 0.18, summary_did["mean_abs_coef"], height=0.33, label="平均|系数|")
axC.barh(ypos + 0.18, summary_did["sig_rate"], height=0.33, label="显著比例")
axC.set_yticks(ypos)
axC.set_yticklabels(summary_did.index)
axC.set_title("C. 处理变量足迹", loc="left", fontproperties=fp_bold, fontsize=13)
axC.legend(frameon=False, prop=fp, fontsize=8)
for t in axC.get_xticklabels() + axC.get_yticklabels():
    t.set_fontproperties(fp)

axD = fig.add_subplot(gs[1, 0])
vals = [spec.loc[spec["depvar"] == d, "coef"].values for d in dep_order]
axD.boxplot(vals, vert=False, labels=dep_order, patch_artist=False)
for i, d in enumerate(dep_order, start=1):
    ss = spec.loc[spec["depvar"] == d, "coef"]
    yy = np.full(len(ss), i) + np.random.uniform(-0.12, 0.12, len(ss))
    axD.scatter(ss, yy, s=15, alpha=0.42)
axD.axvline(0, linewidth=1)
axD.set_title("D. 不同结果变量的规格分布", loc="left", fontproperties=fp_bold, fontsize=13)
axD.set_xlabel("系数", fontproperties=fp)
for t in axD.get_xticklabels() + axD.get_yticklabels():
    t.set_fontproperties(fp)

axE = fig.add_subplot(gs[1, 1:])
yy = np.arange(len(summary_dep))
axE.barh(yy - 0.18, summary_dep["pos_sig"], height=0.33, label="正向显著")
axE.barh(yy + 0.18, summary_dep["neg_sig"], height=0.33, label="负向显著")
for i, (_, r) in enumerate(summary_dep.iterrows()):
    axE.text(max(r["pos_sig"], r["neg_sig"]) + 0.1, i, f"总规格={int(r['total_specs'])}", va="center", fontproperties=fp, fontsize=9)
axE.set_yticks(yy)
axE.set_yticklabels(summary_dep.index)
axE.set_title("E. 各结果变量的显著规格计数", loc="left", fontproperties=fp_bold, fontsize=13)
axE.legend(frameon=False, prop=fp, fontsize=8)
for t in axE.get_xticklabels() + axE.get_yticklabels():
    t.set_fontproperties(fp)

axF = fig.add_subplot(gs[2, :], sharex=axA)
rows = dep_order + did_order + source_order + ["显著(10%)", "显著(5%)"]
row_to_y = {name: len(rows)-1-i for i, name in enumerate(rows)}
for _, r in spec.iterrows():
    x = r["x"]
    axF.scatter(x, row_to_y[r["depvar"]], s=12)
    axF.scatter(x, row_to_y[r["did_var"]], s=12)
    axF.scatter(x, row_to_y[r["source"]], s=12)
    if r["sig10"]:
        axF.scatter(x, row_to_y["显著(10%)"], s=12)
    if r["sig"]:
        axF.scatter(x, row_to_y["显著(5%)"], s=12)
axF.set_yticks(list(row_to_y.values()))
axF.set_yticklabels(list(row_to_y.keys()))
axF.set_xlabel("规格排序（按系数从低到高）", fontproperties=fp)
axF.set_title("F. 规格构成矩阵", loc="left", fontproperties=fp_bold, fontsize=13)
for t in axF.get_xticklabels() + axF.get_yticklabels():
    t.set_fontproperties(fp)

fig.suptitle("样图4（升级重做版）｜核心识别结果的多层 specification dashboard", fontproperties=fp_bold, fontsize=17, y=0.985)
fig.text(
    0.01, 0.01,
    "说明：在原先单一 specification curve 基础上，扩展为“系数云图 + 局部趋势 + 处理变量足迹 + 结果变量分布 + 显著规格计数 + 规格矩阵”六层结构；\n"
    "中文采用精确字体文件路径，适合直接复用到本地环境继续调整。",
    fontproperties=fp, fontsize=10
)
fig.tight_layout(rect=[0, 0.03, 1, 0.965])
fig.savefig("sample_fig4_specification_dashboard_fancy_exact.png", bbox_inches="tight")
fig.savefig("sample_fig4_specification_dashboard_fancy_exact.pdf", bbox_inches="tight")
print("Done.")
