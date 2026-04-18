
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.patches import FancyArrowPatch, Circle, Rectangle, PathPatch
from matplotlib.path import Path

mpl.rcParams['font.sans-serif'] = ['Noto Sans CJK SC', 'Microsoft YaHei', 'SimHei', 'Arial Unicode MS', 'DejaVu Sans']
mpl.rcParams['axes.unicode_minus'] = False
mpl.rcParams.update({
    'font.size': 11,
    'axes.titlesize': 14,
    'axes.labelsize': 11,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'savefig.bbox': 'tight'
})

INK='#222222'; NAVY='#355C7D'; TEAL='#6C8A91'; WINE='#8C3D3D'
GOLD='#B48A3D'; A_COL='#4F6D7A'; B_COL='#8C3D3D'; C_COL='#7C6F64'; GREY='#B9BEC5'


def savefig(fig, out_dir, name):
    fig.savefig(os.path.join(out_dir, f'{name}.png'), dpi=300, facecolor='white')
    fig.savefig(os.path.join(out_dir, f'{name}.pdf'), dpi=300, facecolor='white')
    plt.close(fig)


def main(base_dir=None):
    if base_dir is None:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    input_dir = os.path.join(base_dir, 'input_data')
    out_dir = os.path.join(base_dir, 'charts_regenerated')
    os.makedirs(out_dir, exist_ok=True)

    qual_path = os.path.join(input_dir, 'part3_qualitative_coding.xlsx')
    dict_path = os.path.join(input_dir, 'part3_dictionary_seed_words.xlsx')
    w2v_path = os.path.join(input_dir, 'part3_word2vec_expansion.xlsx')
    ber_path = os.path.join(input_dir, 'part3_bertopic_results.xlsx')
    sup_path = os.path.join(input_dir, 'part3_supervised_enhancement.xlsx')

    qual_cov = pd.read_excel(qual_path, sheet_name='二级类目覆盖率')
    cooc = pd.read_excel(qual_path, sheet_name='同句群共现矩阵长表')
    dict_all = pd.read_excel(dict_path, sheet_name='全量候选词')
    w2v_sugg = pd.read_excel(w2v_path, sheet_name='建议扩展词')
    w2v_noise = pd.read_excel(w2v_path, sheet_name='不纳入噪声词示例')
    w2v_v2 = pd.read_excel(w2v_path, sheet_name='合并后词典V2建议版')
    topic_year = pd.read_excel(ber_path, sheet_name='年度主题分布')
    topic_total = pd.read_excel(ber_path, sheet_name='主题总表')
    sup_model = pd.read_excel(sup_path, sheet_name='模型比较总表')
    sup_label = pd.read_excel(sup_path, sheet_name='分标签指标')

    # Figure 3-1
    df = qual_cov.copy().sort_values('覆盖率', ascending=True)
    colors = [A_COL if x == 'A' else B_COL if x == 'B' else C_COL for x in df['一级维度']]
    fig, ax = plt.subplots(figsize=(9, 6))
    y = np.arange(len(df))
    ax.barh(y, df['覆盖率'] * 100, color=colors, height=0.55, alpha=0.9)
    for yi, val in zip(y, df['覆盖率'] * 100):
        ax.text(val + 1, yi, f'{val:.1f}%', va='center', ha='left', fontsize=9, color=INK)
    ax.set_yticks(y)
    ax.set_yticklabels([f"{c}  {n}" for c, n in zip(df['二级代码'], df['类目名称'])])
    ax.set_xlabel('覆盖率（%）')
    ax.set_xlim(0, 110)
    ax.grid(False)
    ax.spines[['top', 'right']].set_visible(False)
    ax2 = ax.twiny()
    sizes = 40 + (df['平均命中句群数'] - df['平均命中句群数'].min()) / (df['平均命中句群数'].max() - df['平均命中句群数'].min() + 1e-9) * 220
    ax2.scatter(df['强命中率'] * 100, y, s=sizes, color=WINE, alpha=0.78, edgecolor='white', linewidth=0.8)
    ax2.set_xlim(0, 110)
    ax2.set_xlabel('强命中率（%）')
    ax2.grid(False)
    ax2.spines[['bottom', 'right']].set_visible(False)
    ax.set_title('图3-1 二级类目覆盖广度与强命中强度', pad=12)
    ax.text(0, -1.05, '条形表示覆盖率；红点表示强命中率；点大小表示平均命中句群数。', fontsize=9, color='#555555')
    savefig(fig, out_dir, 'Figure_3_1_code_coverage_strength')

    # Figure 3-3
    edges = cooc.sort_values('同句群共现数', ascending=False).copy()
    nodes = ['A1', 'A2', 'B1', 'B2', 'B3', 'B4', 'C1', 'C2', 'C3']
    pos = {'A1': (0.1, 0.75), 'A2': (0.1, 0.35), 'B1': (0.5, 0.88), 'B2': (0.5, 0.63), 'B3': (0.5, 0.37), 'B4': (0.5, 0.12), 'C1': (0.9, 0.75), 'C2': (0.9, 0.5), 'C3': (0.9, 0.25)}
    node_label_map = dict(zip(qual_cov['二级代码'], qual_cov['类目名称']))
    node_sizes = (qual_cov.set_index('二级代码')['覆盖文档数'] * 6).to_dict()
    dim_map = qual_cov.set_index('二级代码')['一级维度'].to_dict()
    fig, ax = plt.subplots(figsize=(10, 6)); ax.axis('off')
    maxw = edges['同句群共现数'].max()
    for _, r in edges.head(18).iterrows():
        x1, y1 = pos[r['code1']]; x2, y2 = pos[r['code2']]
        rad = 0.2 if x1 != x2 else 0.0
        e = FancyArrowPatch((x1, y1), (x2, y2), arrowstyle='-', connectionstyle=f"arc3,rad={rad if y1<y2 else -rad}", linewidth=0.8 + 5 * r['同句群共现数'] / maxw, color='#BDBDBD', alpha=0.45)
        ax.add_patch(e)
    for n in nodes:
        color = A_COL if dim_map[n] == 'A' else B_COL if dim_map[n] == 'B' else C_COL
        circ = Circle(pos[n], radius=0.035 + node_sizes[n] / 2500, facecolor=color, edgecolor='white', linewidth=1.2)
        ax.add_patch(circ)
        ax.text(*pos[n], n, ha='center', va='center', color='white', fontsize=10, fontweight='bold')
        ha = 'right' if pos[n][0] < 0.5 else 'left' if pos[n][0] > 0.5 else 'center'
        dx = -0.065 if pos[n][0] < 0.5 else 0.065 if pos[n][0] > 0.5 else 0
        ax.text(pos[n][0] + dx, pos[n][1], node_label_map[n], ha=ha, va='center', fontsize=9, color=INK)
    top5 = edges.head(5)[['code1', 'code2', '同句群共现数']]
    annot = '最高共现：' + '； '.join([f"{a}-{b}({c})" for a, b, c in top5.itertuples(index=False)])
    ax.text(0.02, 0.02, annot, transform=ax.transAxes, fontsize=9, color='#555555')
    ax.set_title('图3-3 二级代码的同句群共现结构', pad=10)
    savefig(fig, out_dir, 'Figure_3_3_code_cooccurrence_network')

    # Figure 3-4
    df = dict_all.copy()
    df['来源类型简'] = np.where(df['来源类型'].astype(str).str.contains('语料'), '语料扩展', '核心触发词')
    df['最终建议简'] = df['最终建议'].replace({'保留（政策关键低频词）': '保留'})
    left_order = ['核心触发词', '语料扩展']; right_order = ['保留', '观察', '暂不纳入']
    ct = pd.crosstab(df['来源类型简'], df['最终建议简']).reindex(index=left_order, columns=right_order, fill_value=0)
    left_tot = ct.sum(axis=1); right_tot = ct.sum(axis=0)
    fig, ax = plt.subplots(figsize=(10, 6)); ax.axis('off')
    xL, xR = 0.12, 0.88; barw = 0.08
    left_y = {}; cum = 0.88
    for cat, val in left_tot.items():
        h = 0.72 * val / left_tot.sum(); left_y[cat] = (cum - h, cum); cum -= h + 0.04
    right_y = {}; cum = 0.88
    for cat, val in right_tot.items():
        h = 0.72 * val / right_tot.sum(); right_y[cat] = (cum - h, cum); cum -= h + 0.04
    src_colors = {'核心触发词': NAVY, '语料扩展': TEAL}
    tgt_colors = {'保留': NAVY, '观察': GOLD, '暂不纳入': WINE}
    for cat, (y0, y1) in left_y.items():
        ax.add_patch(Rectangle((xL - barw / 2, y0), barw, y1 - y0, facecolor=src_colors[cat], edgecolor='white'))
        ax.text(xL - 0.08, (y0 + y1) / 2, f"{cat}\n(n={left_tot[cat]})", ha='right', va='center', fontsize=10)
    for cat, (y0, y1) in right_y.items():
        ax.add_patch(Rectangle((xR - barw / 2, y0), barw, y1 - y0, facecolor=tgt_colors.get(cat, GREY), edgecolor='white'))
        ax.text(xR + 0.08, (y0 + y1) / 2, f"{cat}\n(n={right_tot[cat]})", ha='left', va='center', fontsize=10)
    left_cursor = {k: v[0] for k, v in left_y.items()}; right_cursor = {k: v[0] for k, v in right_y.items()}
    for src in left_order:
        for tgt in right_order:
            val = int(ct.loc[src, tgt])
            if val == 0:
                continue
            hL = (left_y[src][1] - left_y[src][0]) * val / left_tot[src]
            hR = (right_y[tgt][1] - right_y[tgt][0]) * val / right_tot[tgt]
            y0l = left_cursor[src]; y1l = y0l + hL
            y0r = right_cursor[tgt]; y1r = y0r + hR
            verts = [(xL + barw / 2, y0l), (0.36, y0l), (0.64, y0r), (xR - barw / 2, y0r), (xR - barw / 2, y1r), (0.64, y1r), (0.36, y1l), (xL + barw / 2, y1l), (xL + barw / 2, y0l)]
            codes = [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4, Path.LINETO, Path.CURVE4, Path.CURVE4, Path.CURVE4, Path.CLOSEPOLY]
            ax.add_patch(PathPatch(Path(verts, codes), facecolor=tgt_colors.get(tgt, GREY), alpha=0.38, edgecolor='none'))
            if val >= 6:
                ax.text(0.5, (max(y0l, y0r) + min(y1l, y1r)) / 2, f'{val}', ha='center', va='center', fontsize=9, color=INK)
            left_cursor[src] = y1l; right_cursor[tgt] = y1r
    ax.set_title('图3-4 词典候选词的来源与最终保留路径', pad=12)
    ax.text(0.5, 0.04, '左侧为词项来源，右侧为最终处理结果；中间流带宽度表示词项数量。', ha='center', fontsize=9, color='#555555')
    savefig(fig, out_dir, 'Figure_3_4_dictionary_workflow')

    # Figure 3-8
    cand = len(w2v_sugg)
    retained_words = set(w2v_v2.loc[w2v_v2['来源类型'].astype(str).str.contains('Word2Vec', na=False), '词项'])
    retained = int(w2v_sugg['扩展词'].isin(retained_words).sum())
    filtered = cand - retained
    noise_examples = len(w2v_noise)
    fig, ax = plt.subplots(figsize=(9, 5.5)); ax.axis('off')
    stage_labels = ['Word2Vec候选扩展词', '人工复核后保留', '人工筛除/未纳入']; counts = [cand, retained, filtered]; colors = [NAVY, TEAL, WINE]
    ys = [0.78, 0.5, 0.22]; maxc = max(counts)
    for y, stage, count, color in zip(ys, stage_labels, counts, colors):
        w = 0.7 * count / maxc; x = 0.5 - w / 2
        ax.add_patch(Rectangle((x, y - 0.08), w, 0.16, facecolor=color, edgecolor='white'))
        ax.text(0.5, y, f'{stage}\n{count}', ha='center', va='center', fontsize=12, fontweight='bold', color='white')
    for y1, y2 in zip(ys[:-1], ys[1:]):
        ax.annotate('', xy=(0.5, y2 + 0.1), xytext=(0.5, y1 - 0.1), arrowprops=dict(arrowstyle='-|>', color='#666666', lw=1.2))
    ax.set_title('图3-8 Word2Vec扩展词的筛选与去噪', pad=12)
    ax.text(0.5, 0.04, f'建议扩展词共 {cand} 个，最终纳入 V2 词典 {retained} 个；噪声示例表共展示 {noise_examples} 条。', ha='center', fontsize=9, color='#555555')
    savefig(fig, out_dir, 'Figure_3_8_expansion_screening_funnel')

    # Figure 3-9
    topic_wide = topic_year.pivot_table(index='year', columns='topic', values='年份主题占比', fill_value=0).sort_index()
    topic_counts = topic_total.set_index('主题编号')['文档数'].to_dict()
    topic_names = topic_total.set_index('主题编号')['主题名称'].to_dict()
    fig, axes = plt.subplots(2, 5, figsize=(14, 6), sharex=True, sharey=True); axes = axes.flatten()
    for i, topic in enumerate(sorted(topic_wide.columns)):
        ax = axes[i]
        y = topic_wide[topic].values
        ax.fill_between(topic_wide.index, 0, y, color=NAVY, alpha=0.25)
        ax.plot(topic_wide.index, y, color=NAVY, lw=2)
        ax.set_title(f'Topic {topic}', fontsize=11, pad=3)
        ax.text(0.03, 0.9, f'n={topic_counts.get(topic,0)}', transform=ax.transAxes, fontsize=8.5, color=WINE)
        short = ' / '.join(str(topic_names[topic]).split('_')[1:3])
        ax.text(0.03, 0.77, short, transform=ax.transAxes, fontsize=8, color='#555555')
        ax.spines[['top', 'right']].set_visible(False); ax.grid(False)
        ax.set_ylim(0, max(topic_wide.max()) * 1.1)
    for ax in axes:
        ax.set_xticks(sorted(topic_wide.index)[::2]); ax.tick_params(axis='x', rotation=45)
    fig.suptitle('图3-9 BERTopic 主题的时间演化（分主题面板）', y=0.99, fontsize=14)
    fig.text(0.5, 0.01, '每个小面板展示一个主题在不同年份中的占比变化；阴影面积越大表示该主题当年权重越高。', ha='center', fontsize=9, color='#555555')
    savefig(fig, out_dir, 'Figure_3_9_topic_dynamics_panels')

    # Figure 3-14
    best_model = sup_model.sort_values('micro_f1', ascending=False).iloc[0]['model']
    lab = sup_label[sup_label['model'] == best_model].copy()
    labels_order = ['A1', 'A2', 'B1', 'B2', 'B3', 'B4', 'C1', 'C2', 'C3']
    lab['label'] = pd.Categorical(lab['label'], categories=labels_order, ordered=True)
    lab = lab.sort_values('label')
    fig, axes = plt.subplots(3, 3, figsize=(11, 8), sharex=True); axes = axes.flatten()
    for ax, (_, r) in zip(axes, lab.iterrows()):
        p = float(r['precision']); rec = float(r['recall']); f1 = float(r['f1']); sup = int(r['support'])
        ax.hlines(0, min(p, rec), max(p, rec), color='#9AA1A8', lw=3)
        ax.scatter([p], [0], s=90, color=NAVY, zorder=3)
        ax.scatter([rec], [0], s=90, color=WINE, zorder=3)
        ax.set_xlim(0, 1); ax.set_ylim(-0.8, 0.8); ax.set_yticks([])
        ax.set_title(str(r['label']), fontsize=11, loc='left')
        ax.text(0.02, 0.68, f'F1={f1:.3f}\n支持数={sup}', transform=ax.transAxes, fontsize=8.5, color='#555555')
        ax.spines[['top', 'right', 'left']].set_visible(False); ax.grid(False)
    for i, ax in enumerate(axes):
        if i < 6: ax.tick_params(labelbottom=False)
    fig.suptitle(f'图3-14 最佳模型（{best_model}）在九个标签上的识别能力', y=0.995, fontsize=14)
    fig.text(0.5, 0.01, '横轴为指标值；蓝点为 Precision，酒红点为 Recall，连线长度反映二者差距。', ha='center', fontsize=9, color='#555555')
    savefig(fig, out_dir, 'Figure_3_14_labelwise_dumbbell_grid')

    print('Done. Output to:', out_dir)

if __name__ == '__main__':
    main()
