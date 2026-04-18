
import os, math, pandas as pd, numpy as np, re
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import PathPatch
from matplotlib.path import Path as MplPath
from sklearn.decomposition import PCA

BASE = Path(__file__).resolve().parent.parent
INPUT = BASE / "input_data"
OUTPUT = BASE / "charts_regenerated"
OUTPUT.mkdir(exist_ok=True)

def setup_fonts():
    candidates = [
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    ]
    for p in candidates:
        if os.path.exists(p):
            prop = fm.FontProperties(fname=p)
            plt.rcParams["font.family"] = prop.get_name()
            break
    plt.rcParams["axes.unicode_minus"] = False

def savefig(fig, stem):
    for ext in ['png','pdf','svg']:
        fig.savefig(OUTPUT/f'{stem}.{ext}', dpi=320, bbox_inches='tight')
    plt.close(fig)

def softmax_rows(arr):
    arr = arr - arr.max(axis=1, keepdims=True)
    e = np.exp(arr)
    return e/e.sum(axis=1, keepdims=True)

def draw_ternary(df):
    work = df.copy()
    cols = ['z_A_idx','z_B_idx','z_C_idx'] if set(['z_A_idx','z_B_idx','z_C_idx']).issubset(work.columns) else ['A_idx','B_idx','C_idx']
    P = softmax_rows(work[cols].to_numpy(float))
    work[['pA','pB','pC']] = P
    sqrt3 = math.sqrt(3)
    A=np.array([0.5,sqrt3/2]); B=np.array([0.0,0.0]); C=np.array([1.0,0.0])
    xy = work['pA'].to_numpy()[:,None]*A + work['pB'].to_numpy()[:,None]*B + work['pC'].to_numpy()[:,None]*C
    work['x'],work['y']=xy[:,0],xy[:,1]
    top_provs=[p for p in work.groupby('province')['doc_count'].sum().sort_values(ascending=False).index if p!='中央'][:5]
    track_cols=['#264653','#8D5524','#6D597A','#B56576','#4D908E']
    fig,ax=plt.subplots(figsize=(10,8.8))
    tri=np.vstack([B,C,A,B]); ax.plot(tri[:,0],tri[:,1],color='#444',lw=1)
    for t in [0.2,0.4,0.6,0.8]:
        pts=[t*A+(1-t)*B,t*A+(1-t)*C]; ax.plot([p[0] for p in pts],[p[1] for p in pts],color='#e4e4e4',lw=.6,zorder=0)
        pts=[t*B+(1-t)*A,t*B+(1-t)*C]; ax.plot([p[0] for p in pts],[p[1] for p in pts],color='#e4e4e4',lw=.6,zorder=0)
        pts=[t*C+(1-t)*A,t*C+(1-t)*B]; ax.plot([p[0] for p in pts],[p[1] for p in pts],color='#e4e4e4',lw=.6,zorder=0)
    sc=ax.scatter(work['x'],work['y'],c=work['year'],cmap='cividis',s=18+2*np.sqrt(work['doc_count']),alpha=.6,edgecolors='white',linewidths=.4)
    for c,p in zip(track_cols,top_provs):
        dfp=work[work['province']==p].sort_values('year')
        ax.plot(dfp['x'],dfp['y'],color=c,lw=1.6)
        ax.scatter(dfp['x'],dfp['y'],s=30,color=c,edgecolors='white',linewidths=.4)
        if len(dfp):
            lr=dfp.iloc[-1]; ax.text(lr['x']+.015,lr['y']+.008,p,fontsize=9,color=c)
    ax.text(A[0],A[1]+.045,'A: 治理数字化接口',ha='center',va='bottom',fontsize=12,weight='bold')
    ax.text(B[0]-.035,B[1]-.03,'B: 规范治理',ha='left',va='top',fontsize=12,weight='bold')
    ax.text(C[0]+.035,C[1]-.03,'C: 风险识别',ha='right',va='top',fontsize=12,weight='bold')
    ax.text(.02,.97,'每个点 = 一个省—年观测\n位置由 A/B/C 三类指数归一化后确定\n点大小 = 文本数量，颜色 = 年份',transform=ax.transAxes,va='top',fontsize=10,
            bbox=dict(boxstyle='round,pad=.25',facecolor='white',edgecolor='#cccccc'))
    cbar=fig.colorbar(sc,ax=ax,fraction=.03,pad=.03); cbar.set_label('年份')
    ax.set_title('图4-A 省—年PPP政策状态三元图',fontsize=15,pad=14,weight='bold'); ax.axis('off'); ax.set_xlim(-.08,1.08); ax.set_ylim(-.08,A[1]+.1)
    fig.tight_layout(); savefig(fig,'Figure_4A_policy_state_ternary')

def draw_embedding(df):
    topic_cols=[c for c in df.columns if re.fullmatch(r'topic_\d+_share',c)]
    X=df[topic_cols].fillna(0).to_numpy(float)
    pca=PCA(n_components=2, random_state=42)
    coords=pca.fit_transform(X)
    emb=df.copy(); emb['pc1'],emb['pc2']=coords[:,0],coords[:,1]
    emb['year_stage']=pd.cut(emb['year'],bins=[2013,2016,2019,2022,2026],labels=['2014-2016','2017-2019','2020-2022','2023-2025'],include_lowest=True)
    top_provs=[p for p in emb.groupby('province')['doc_count'].sum().sort_values(ascending=False).index if p!='中央'][:5]
    track_cols=['#264653','#8D5524','#6D597A','#B56576','#4D908E']
    fig,ax=plt.subplots(figsize=(10.5,8.2))
    sc=ax.scatter(emb['pc1'],emb['pc2'],c=emb['ppp_governance_capacity_index'],cmap='viridis',s=16+2*np.sqrt(emb['doc_count']),alpha=.75,edgecolors='white',linewidths=.35)
    cent=emb.groupby('year_stage', observed=True)[['pc1','pc2']].mean().reset_index()
    ax.plot(cent['pc1'],cent['pc2'],color='#8b1e3f',lw=1.5,ls='--'); ax.scatter(cent['pc1'],cent['pc2'],s=50,color='#8b1e3f')
    for _,r in cent.iterrows():
        ax.text(r['pc1']+.008,r['pc2']+.008,str(r['year_stage']),fontsize=9,color='#8b1e3f')
    for c,p in zip(track_cols,top_provs):
        dfp=emb[emb['province']==p].sort_values('year')
        ax.plot(dfp['pc1'],dfp['pc2'],color=c,lw=1.1,alpha=.85)
        if len(dfp):
            lr=dfp.iloc[-1]; ax.text(lr['pc1']+.006,lr['pc2']+.006,p,fontsize=9,color=c)
    ax.axhline(0,color='#d8d8d8',lw=.8); ax.axvline(0,color='#d8d8d8',lw=.8)
    cbar=fig.colorbar(sc,ax=ax,fraction=.03,pad=.03); cbar.set_label('综合治理能力指数')
    ax.text(.02,.98,f'输入向量 = 10个 topic shares\n降维方法 = PCA\nPC1 = {pca.explained_variance_ratio_[0]:.1%}\nPC2 = {pca.explained_variance_ratio_[1]:.1%}',transform=ax.transAxes,va='top',fontsize=10,
            bbox=dict(boxstyle='round,pad=.25',facecolor='white',edgecolor='#cccccc'))
    ax.set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.1%})'); ax.set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.1%})')
    ax.set_title('图4-B 基于 topic-share 向量的省—年政策状态嵌入图',fontsize=15,pad=14,weight='bold')
    ax.spines[['top','right']].set_visible(False); fig.tight_layout(); savefig(fig,'Figure_4B_topicshare_embedding_pca')

def draw_bridge(doc):
    topic_dim=(doc.groupby(['topic','topic_main_dimension']).size().reset_index(name='n'))
    topic_dim=topic_dim[topic_dim['topic'].notna() & topic_dim['topic_main_dimension'].notna()].copy()
    topic_sizes=topic_dim.groupby('topic')['n'].sum().sort_values(ascending=False)
    dims=['A','B','C']; left_y={}; right_y={'A':0.78,'B':0.5,'C':0.22}
    total=topic_sizes.sum(); cum=0
    for t,n in topic_sizes.items():
        h=n/total*0.72
        left_y[t]=0.86-cum-h/2
        cum+=h+0.01
    fig,ax=plt.subplots(figsize=(11,8)); ax.axis('off')
    dim_map={'A':'#355C7D','B':'#7A4E2D','C':'#6C757D'}
    for t,n in topic_sizes.items():
        y=left_y[t]
        ax.add_patch(plt.Rectangle((0.06,y-0.018),0.04,0.036,color='#506D84',alpha=.9))
        ax.text(0.105,y,f'T{int(t)}',va='center',fontsize=9)
    for d in dims:
        y=right_y[d]
        ax.add_patch(plt.Rectangle((0.86,y-0.03),0.05,0.06,color=dim_map[d],alpha=.95))
        ax.text(0.845,y,{'A':'A:数字化接口','B':'B:规范治理','C':'C:风险识别'}[d],va='center',ha='right',fontsize=11,weight='bold',color=dim_map[d])
    for _,r in topic_dim.iterrows():
        t=r['topic']; d=str(r['topic_main_dimension'])[0]
        if d not in dims or t not in left_y: continue
        y0=left_y[t]; y1=right_y[d]
        width=0.2+2.6*(r['n']/topic_dim['n'].max())
        verts=[(0.10,y0),(0.35,y0),(0.62,y1),(0.86,y1)]
        path=MplPath(verts,[MplPath.MOVETO,MplPath.CURVE4,MplPath.CURVE4,MplPath.CURVE4])
        patch=PathPatch(path, facecolor='none', edgecolor=dim_map[d], lw=width, alpha=.30, capstyle='round')
        ax.add_patch(patch)
    ax.text(0.06,0.95,'主题变量',fontsize=12,weight='bold'); ax.text(0.72,0.95,'制度维度',fontsize=12,weight='bold')
    ax.text(0.02,0.08,'边宽表示文档级映射强度。该图用于展示第3部分主题识别结果如何回译到 A/B/C 制度维度。',fontsize=10,
            bbox=dict(boxstyle='round,pad=.25',facecolor='white',edgecolor='#cccccc'))
    ax.set_title('图4-7 主题变量向制度维度变量的桥梁图',fontsize=15,pad=14,weight='bold')
    fig.tight_layout(); savefig(fig,'Figure_4_7_topic_to_dimension_bridge')

def draw_parallel(pv):
    cols=['A1_idx','A2_idx','B1_idx','B2_idx','B3_idx','B4_idx','C1_idx','C2_idx','C3_idx','ppp_governance_capacity_index']
    pc=pv[cols+['province','year','doc_count']].dropna().copy()
    pc['group']=pd.qcut(pc['ppp_governance_capacity_index'],3,labels=['低','中','高'])
    sampled=pd.concat([g.sample(min(len(g),12), random_state=42) for _,g in pc.groupby('group', observed=True)])
    x=np.arange(len(cols)); fig,ax=plt.subplots(figsize=(13,7.5))
    group_colors={'低':'#9e9e9e','中':'#6C8EBF','高':'#7A1F1F'}
    minv=pc[cols].min(); maxv=pc[cols].max(); rng=(maxv-minv).replace(0,1)
    for _,row in sampled.iterrows():
        y=((row[cols]-minv)/rng).to_numpy()
        ax.plot(x,y,color=group_colors[row['group']],alpha=0.35,lw=1.2)
    for grp,color in group_colors.items():
        med = pc[pc['group']==grp][cols].median()
        y=((med-minv)/rng).to_numpy()
        ax.plot(x,y,color=color,lw=2.8,label=f'{grp}治理能力组中位线')
    ax.set_xticks(x); ax.set_xticklabels(['A1','A2','B1','B2','B3','B4','C1','C2','C3','治理能力'],fontsize=10)
    ax.set_yticks([0,.25,.5,.75,1.0]); ax.set_yticklabels(['低','','中','','高'])
    ax.set_xlim(x.min(),x.max()); ax.set_ylim(0,1)
    for xi in x: ax.axvline(xi,color='#e8e8e8',lw=.8,zorder=0)
    ax.legend(frameon=False, loc='upper left')
    ax.text(0.01,0.98,'浅线为代表性省—年观测，粗线为各治理能力组中位结构。',transform=ax.transAxes,va='top',fontsize=10,
            bbox=dict(boxstyle='round,pad=.25',facecolor='white',edgecolor='#cccccc'))
    ax.set_title('图4-8 综合治理能力指数的多维结构图',fontsize=15,pad=14,weight='bold')
    ax.spines[['top','right']].set_visible(False); fig.tight_layout(); savefig(fig,'Figure_4_8_composite_parallel_coordinates')

def draw_heatmap(pv):
    heat = pv.pivot(index='province', columns='year', values='ppp_governance_capacity_index')
    heat = heat.loc[heat.mean(axis=1).sort_values(ascending=False).index]
    fig,ax=plt.subplots(figsize=(10,10))
    im=ax.imshow(heat.fillna(np.nan).to_numpy(), aspect='auto', cmap='Blues')
    ax.set_xticks(np.arange(len(heat.columns))); ax.set_xticklabels(heat.columns, rotation=45, ha='right')
    ax.set_yticks(np.arange(len(heat.index))); ax.set_yticklabels(heat.index, fontsize=9)
    ax.set_title('图4-5 PPP治理能力指数的省—年分布热区',fontsize=15,pad=14,weight='bold')
    cbar=fig.colorbar(im,ax=ax,fraction=.03,pad=.03); cbar.set_label('治理能力指数')
    ax.text(0.01,-0.08,'按各省样本期平均治理能力指数由高到低排序。',transform=ax.transAxes,fontsize=10)
    fig.tight_layout(); savefig(fig,'Figure_4_5_province_year_capacity_heatmap')

def main():
    setup_fonts()
    pv = pd.read_csv(INPUT/'part4_province_year_variables.csv')
    xl = pd.ExcelFile(INPUT/'part4_text_variable_construction_results.xlsx')
    doc = pd.read_excel(xl, sheet_name='文档级变量')
    draw_ternary(pv); draw_embedding(pv); draw_bridge(doc); draw_parallel(pv); draw_heatmap(pv)

if __name__ == '__main__':
    main()
