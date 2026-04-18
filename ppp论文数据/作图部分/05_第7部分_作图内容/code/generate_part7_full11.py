
import os, math, json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Rectangle

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
INPUT_DIR = os.path.join(BASE_DIR, "input_data")
CHART_DIR = os.path.join(BASE_DIR, "charts_regenerated")
os.makedirs(CHART_DIR, exist_ok=True)

palette = {
    'blue':'#3C5A99', 'red':'#8F3B3B', 'teal':'#3B7A78', 'gold':'#B08A3E',
    'purple':'#6C5B7B', 'gray':'#4A4A4A', 'light':'#BFC7D5', 'green':'#4F7C4B'
}
het_type_map = {
    'digital_econ_high_vs_low':'Digital economy',
    'dfi_high_vs_low':'Digital finance',
    'A_idx_high_vs_low':'A-index base',
    'governance_capacity_high_vs_low':'Governance base'
}
outcome_map = {'ppp_quality_pca_rebuilt':'PCA quality','ppp_quality_pca_rebuilt_fixed':'PCA quality',
               'exec_share':'Execution share','proc_share':'Procurement share'}

plt.rcParams.update({
    'font.family':'DejaVu Sans',
    'font.size':10,
    'axes.titlesize':13,
    'axes.labelsize':11,
    'figure.facecolor':'white',
    'axes.facecolor':'white',
    'axes.edgecolor':'#222222',
    'axes.grid':False,
    'savefig.facecolor':'white',
    'savefig.bbox':'tight'
})

def savefig_multi(fig, stem):
    for ext in ['png','pdf','svg']:
        fig.savefig(os.path.join(CHART_DIR, f'{stem}.{ext}'), dpi=300 if ext=='png' else None, bbox_inches='tight')
    plt.close(fig)

def load_data():
    xl1 = pd.ExcelFile(os.path.join(INPUT_DIR, 'part7_1to4_heterogeneity.xlsx'))
    het_all = xl1.parse('全部异质性结果')
    het_sum = xl1.parse('交互项摘要')
    het_sum['het_label'] = het_sum['heterogeneity_type'].map(het_type_map)
    het_sum['outcome_label'] = het_sum['outcome'].map(outcome_map)

    xl2 = pd.ExcelFile(os.path.join(INPUT_DIR, 'part7_5_risk_exposure.xlsx'))
    risk_comp = xl2.parse('风险暴露指数构造')
    risk_inter = xl2.parse('交互项摘要')
    risk_all = xl2.parse('全部结果')
    risk_inter['outcome_label'] = risk_inter['outcome'].map(outcome_map)
    risk_all['outcome_label'] = risk_all['outcome'].map(outcome_map)

    xl3 = pd.ExcelFile(os.path.join(INPUT_DIR, 'part7_6_gov_open.xlsx'))
    open_reg = xl3.parse('回归结果')
    open_reg['outcome_label'] = open_reg['outcome'].map(outcome_map)
    open_reg['interaction_term'] = open_reg['coef_interaction_or_blank'].fillna(0)
    return het_all, het_sum, risk_comp, risk_inter, risk_all, open_reg

def chart1(het_sum):
    fig, axes = plt.subplots(3,4, figsize=(15,9), sharex=False)
    for r, outcome in enumerate(['PCA quality','Execution share','Procurement share']):
        for c, het in enumerate(['Digital economy','Digital finance','A-index base','Governance base']):
            ax = axes[r,c]
            sub = het_sum[(het_sum.outcome_label==outcome)&(het_sum.het_label==het)]
            if len(sub)==0:
                ax.axis('off'); continue
            row=sub.iloc[0]
            low=row['coef_low_group']; high=row['coef_high_group']; p=row['interaction_p']
            ax.hlines(0.5, low, high, color=palette['gray'], lw=2, alpha=0.8)
            ax.scatter([low],[0.5], s=80, color=palette['blue'], zorder=3)
            ax.scatter([high],[0.5], s=80, color=palette['red'], zorder=3)
            ax.axvline(0,color='#999999', lw=1, ls='--')
            ax.text(low,0.62,f'Low {low:.2f}', ha='center', va='bottom', fontsize=9, color=palette['blue'])
            ax.text(high,0.38,f'High {high:.2f}', ha='center', va='top', fontsize=9, color=palette['red'])
            ax.text(0.98,0.88,f'p={p:.3f}', transform=ax.transAxes, ha='right', va='top', fontsize=9,
                    color=palette['red'] if p<0.1 else palette['gray'])
            ax.set_ylim(0,1)
            ax.set_yticks([])
            ax.set_title(het if r==0 else "")
            if c==0:
                ax.set_ylabel(outcome)
            for spine in ['left','right','top']:
                ax.spines[spine].set_visible(False)
    fig.suptitle('Figure 7-1  Heterogeneity atlas: low-group vs high-group treatment effects', y=1.02, fontsize=15)
    savefig_multi(fig,'Figure_7_1_heterogeneity_atlas_dumbbell')

def chart2(het_sum):
    fig, axes = plt.subplots(1,3, figsize=(15,4), sharey=True)
    for ax, outcome in zip(axes,['PCA quality','Execution share','Procurement share']):
        sub=het_sum[het_sum.outcome_label==outcome].copy().sort_values('interaction_p', ascending=True)
        y=np.arange(len(sub))
        colors=[palette['red'] if p<0.1 else palette['gray'] for p in sub['interaction_p']]
        ax.hlines(y, 0, sub['interaction_p'], color=colors, lw=2)
        ax.scatter(sub['interaction_p'], y, color=colors, s=70, zorder=3)
        ax.axvline(0.1, color='#777777', ls='--', lw=1)
        ax.set_yticks(y); ax.set_yticklabels(sub['het_label'])
        ax.set_xlim(0,1)
        ax.set_title(outcome)
        ax.set_xlabel('Interaction p-value')
        for spine in ['top','right']:
            ax.spines[spine].set_visible(False)
    fig.suptitle('Figure 7-2  Interaction-significance profile across heterogeneity types', y=1.05, fontsize=15)
    savefig_multi(fig,'Figure_7_2_interaction_p_profile')

def chart3(het_sum):
    fig, ax = plt.subplots(figsize=(8,7))
    markers={'PCA quality':'o','Execution share':'s','Procurement share':'^'}
    for outcome in ['PCA quality','Execution share','Procurement share']:
        sub=het_sum[het_sum.outcome_label==outcome]
        sizes=200*np.abs(sub['coef_high_group']-sub['coef_low_group'])+80
        colors=[palette['purple'] if p<0.1 else palette['light'] for p in sub['interaction_p']]
        ax.scatter(sub['coef_low_group'], sub['coef_high_group'], s=sizes, marker=markers[outcome],
                c=colors, edgecolor='#333333', linewidth=0.8, alpha=0.9, label=outcome)
        for _,row in sub.iterrows():
            ax.text(row['coef_low_group'], row['coef_high_group'], row['het_label'].split()[0], fontsize=8,
                    ha='left', va='bottom')
    lims=[min(ax.get_xlim()[0],ax.get_ylim()[0]), max(ax.get_xlim()[1],ax.get_ylim()[1])]
    ax.plot(lims,lims, ls='--', color='#777777', lw=1)
    ax.axvline(0, color='#bbbbbb', lw=1); ax.axhline(0, color='#bbbbbb', lw=1)
    ax.set_xlabel('Low-group effect')
    ax.set_ylabel('High-group effect')
    ax.set_title('Figure 7-3  Effect frontier: low-group vs high-group coefficients')
    for spine in ['top','right']:
        ax.spines[spine].set_visible(False)
    ax.legend(frameon=False, loc='lower right')
    savefig_multi(fig,'Figure_7_3_effect_frontier_scatter')

def chart4(het_all):
    inter_rows=het_all[het_all['spec']=='interaction'].copy()
    inter_rows['gap']=inter_rows['coef_high_minus_low']
    inter_rows['label']=inter_rows['heterogeneity_type'].map(het_type_map)+' | '+inter_rows['outcome'].map(outcome_map)
    inter_rows=inter_rows.sort_values('gap')
    fig, ax = plt.subplots(figsize=(10,7))
    y=np.arange(len(inter_rows))
    colors=[palette['red'] if g>0 else palette['blue'] for g in inter_rows['gap']]
    ax.hlines(y, 0, inter_rows['gap'], color=colors, lw=2)
    ax.scatter(inter_rows['gap'], y, color=colors, s=70)
    ax.axvline(0, color='#777777', ls='--', lw=1)
    ax.set_yticks(y); ax.set_yticklabels(inter_rows['label'])
    ax.set_xlabel('High-group minus low-group effect')
    ax.set_title('Figure 7-4  Ranking of heterogeneity gaps')
    for spine in ['top','right']:
        ax.spines[spine].set_visible(False)
    savefig_multi(fig,'Figure_7_4_gap_ranking_lollipop')

def chart5(risk_comp):
    fig, ax = plt.subplots(figsize=(10,5))
    risk_comp = risk_comp.copy()
    risk_comp['score']=risk_comp['direction'].map({'正向进入风险暴露指数':1,'负向进入风险暴露指数':-1}).fillna(0)
    y=np.arange(len(risk_comp))
    cols=[palette['red'] if s>0 else palette['blue'] for s in risk_comp['score']]
    ax.hlines(y, 0, risk_comp['score'], color=cols, lw=3)
    ax.scatter(risk_comp['score'], y, c=cols, s=90)
    ax.axvline(0, color='#777777', ls='--', lw=1)
    ax.set_yticks(y); ax.set_yticklabels(risk_comp['component'])
    ax.set_xticks([-1,1]); ax.set_xticklabels(['Risk-reducing','Risk-increasing'])
    ax.set_title('Figure 7-5  Construction logic of the risk-exposure proxy')
    for spine in ['top','right']:
        ax.spines[spine].set_visible(False)
    savefig_multi(fig,'Figure_7_5_risk_proxy_polarity')

def chart6(risk_inter):
    fig, ax = plt.subplots(figsize=(8,5))
    sub=risk_inter.copy().sort_values('outcome_label')
    y=np.arange(len(sub))
    for i,row in enumerate(sub.itertuples()):
        ax.hlines(i, row.coef_low_risk, row.coef_high_risk, color=palette['gray'], lw=2)
        ax.scatter(row.coef_low_risk, i, color=palette['blue'], s=80)
        ax.scatter(row.coef_high_risk, i, color=palette['red'], s=80)
        ax.text(row.coef_low_risk, i+0.15, f'Low {row.coef_low_risk:.2f}', color=palette['blue'], fontsize=9, ha='center')
        ax.text(row.coef_high_risk, i-0.15, f'High {row.coef_high_risk:.2f}', color=palette['red'], fontsize=9, ha='center')
        ax.text(0.98, (i+0.1)/len(sub), f'p={row.p_interaction:.3f}', transform=ax.transAxes, ha='right', va='center', fontsize=8)
    ax.axvline(0,color='#777777',ls='--',lw=1)
    ax.set_yticks(y); ax.set_yticklabels(sub['outcome_label'])
    ax.set_title('Figure 7-6  Risk-exposure heterogeneity by outcome')
    for spine in ['top','right']:
        ax.spines[spine].set_visible(False)
    savefig_multi(fig,'Figure_7_6_risk_exposure_dumbbell')

def chart7(risk_all):
    fig, axes = plt.subplots(1,3, figsize=(15,4), sharey=False)
    for ax, outcome in zip(axes,['PCA quality','Execution share','Procurement share']):
        rowi=risk_all[(risk_all['analysis_type']=='interaction') & (risk_all['outcome_label']==outcome)].iloc[0]
        vals=[rowi['coef_low_risk'], rowi['coef_high_minus_low'], rowi['coef_high_risk']]
        labels=['Low-risk','High-low gap','High-risk']
        cols=[palette['blue'], palette['gray'], palette['red']]
        ax.bar(labels, vals, color=cols)
        ax.axhline(0,color='#777777',ls='--',lw=1)
        for j,v in enumerate(vals):
            ax.text(j,v,f'{v:.2f}',ha='center',va='bottom' if v>=0 else 'top',fontsize=9)
        ax.set_title(outcome)
        for spine in ['top','right']:
            ax.spines[spine].set_visible(False)
    fig.suptitle('Figure 7-7  Risk-exposure heterogeneity: low-risk, gap, and high-risk effects', y=1.03, fontsize=15)
    savefig_multi(fig,'Figure_7_7_risk_exposure_decomposition')

def chart8():
    fig, ax = plt.subplots(figsize=(10,5))
    ax.set_xlim(0,1); ax.set_ylim(0,1); ax.axis('off')
    boxes={
        'A1_idx':(0.05,0.7,0.18,0.12),
        'A2_idx':(0.05,0.3,0.18,0.12),
        'Proxy':(0.38,0.5,0.2,0.14),
        'PCA quality':(0.75,0.75,0.2,0.1),
        'Execution share':(0.75,0.5,0.2,0.1),
        'Procurement share':(0.75,0.25,0.2,0.1)
    }
    for name,(x,y,w,h) in boxes.items():
        color=palette['blue'] if 'A' in name else palette['red'] if name=='Proxy' else palette['gray']
        rect=Rectangle((x,y),w,h,facecolor=color if name!='Proxy' else '#EFE7E7',edgecolor='#333333',lw=1.2,alpha=0.9)
        ax.add_patch(rect)
        ax.text(x+w/2,y+h/2,name,ha='center',va='center',fontsize=11)
    def arrow(x1,y1,x2,y2,text=None,color='#777777'):
        arr=FancyArrowPatch((x1,y1),(x2,y2),arrowstyle='-|>',mutation_scale=15,lw=2,color=color,alpha=0.8,
                            connectionstyle="arc3,rad=0.0")
        ax.add_patch(arr)
        if text:
            ax.text((x1+x2)/2,(y1+y2)/2+0.04,text,ha='center',fontsize=9,color=color)
    arrow(0.23,0.76,0.38,0.57,'input',palette['blue'])
    arrow(0.23,0.36,0.38,0.57,'input',palette['blue'])
    arrow(0.58,0.57,0.75,0.80,'heterogeneity',palette['red'])
    arrow(0.58,0.57,0.75,0.55,'heterogeneity',palette['red'])
    arrow(0.58,0.57,0.75,0.30,'heterogeneity',palette['red'])
    ax.set_title('Figure 7-8  Government-data-openness proxy: structure and destination')
    savefig_multi(fig,'Figure_7_8_gov_open_proxy_structure')

def chart9(open_reg):
    low_high=open_reg[open_reg['spec'].isin(['low_open','high_open'])].pivot(index='outcome_label',columns='spec',values='coef_treat_share').reset_index()
    inter_sub=open_reg[open_reg['spec']=='interaction'][['outcome_label','coef_interaction_or_blank','p_value']].rename(columns={'coef_interaction_or_blank':'interaction','p_value':'p'})
    low_high=low_high.merge(inter_sub,on='outcome_label',how='left')
    fig, ax = plt.subplots(figsize=(8,5))
    y=np.arange(len(low_high))
    for i,row in low_high.iterrows():
        ax.hlines(i,row['low_open'],row['high_open'],color=palette['gray'],lw=2)
        ax.scatter(row['low_open'],i,color=palette['blue'],s=80)
        ax.scatter(row['high_open'],i,color=palette['red'],s=80)
        ax.text(row['low_open'],i+0.14,f'Low {row["low_open"]:.2f}',fontsize=9,color=palette['blue'],ha='center')
        ax.text(row['high_open'],i-0.14,f'High {row["high_open"]:.2f}',fontsize=9,color=palette['red'],ha='center')
        ax.text(0.98,(i+0.1)/len(low_high),f'int={row["interaction"]:.2f}, p={row["p"]:.3f}',transform=ax.transAxes,ha='right',va='center',fontsize=8)
    ax.axvline(0,color='#777777',ls='--',lw=1)
    ax.set_yticks(y); ax.set_yticklabels(low_high['outcome_label'])
    ax.set_title('Figure 7-9  Government-data-openness heterogeneity by outcome')
    for spine in ['top','right']:
        ax.spines[spine].set_visible(False)
    savefig_multi(fig,'Figure_7_9_gov_open_dumbbell')

def chart10(het_sum, risk_inter, open_reg):
    low_high=open_reg[open_reg['spec'].isin(['low_open','high_open'])].pivot(index='outcome_label',columns='spec',values='coef_treat_share').reset_index()
    inter_sub=open_reg[open_reg['spec']=='interaction'][['outcome_label','coef_interaction_or_blank','p_value']].rename(columns={'coef_interaction_or_blank':'interaction','p_value':'p'})
    low_high=low_high.merge(inter_sub,on='outcome_label',how='left')
    rows=[]
    for _,r in het_sum.iterrows():
        rows.append([r['het_label'], r['outcome_label'], r['coef_high_group']-r['coef_low_group'], r['interaction_p']])
    for _,r in risk_inter.iterrows():
        rows.append(['Risk exposure', r['outcome_label'], r['coef_high_risk']-r['coef_low_risk'], r['p_interaction']])
    for outcome in ['PCA quality','Execution share','Procurement share']:
        low=low_high[low_high['outcome_label']==outcome].iloc[0]['low_open']
        high=low_high[low_high['outcome_label']==outcome].iloc[0]['high_open']
        p=low_high[low_high['outcome_label']==outcome].iloc[0]['p']
        rows.append(['Gov-data openness', outcome, high-low, p])
    score=pd.DataFrame(rows, columns=['heterogeneity','outcome','gap','p'])
    hets=list(dict.fromkeys(score['heterogeneity']))
    outs=['PCA quality','Execution share','Procurement share']
    fig, ax = plt.subplots(figsize=(10,6))
    for i,h in enumerate(hets):
        for j,o in enumerate(outs):
            row=score[(score['heterogeneity']==h)&(score['outcome']==o)].iloc[0]
            color=palette['red'] if row['gap']>0 else palette['blue']
            alpha=1.0 if row['p']<0.1 else 0.35
            size=150+600*min(abs(row['gap']),1.5)/1.5
            ax.scatter(j, len(hets)-1-i, s=size, color=color, alpha=alpha, edgecolor='#333333')
            ax.text(j, len(hets)-1-i-0.23, f'{row["gap"]:+.2f}', ha='center', va='top', fontsize=8)
    ax.set_xticks(range(len(outs))); ax.set_xticklabels(outs)
    ax.set_yticks(range(len(hets))); ax.set_yticklabels(reversed(hets))
    ax.set_xlim(-0.5,len(outs)-0.5); ax.set_ylim(-0.5,len(hets)-0.5)
    ax.set_title('Figure 7-10  Heterogeneity evidence scorecard')
    for spine in ['top','right']:
        ax.spines[spine].set_visible(False)
    savefig_multi(fig,'Figure_7_10_heterogeneity_scorecard')

def chart11(het_sum, risk_inter, open_reg):
    low_high=open_reg[open_reg['spec'].isin(['low_open','high_open'])].pivot(index='outcome_label',columns='spec',values='coef_treat_share').reset_index()
    inter_sub=open_reg[open_reg['spec']=='interaction'][['outcome_label','coef_interaction_or_blank','p_value']].rename(columns={'coef_interaction_or_blank':'interaction','p_value':'p'})
    low_high=low_high.merge(inter_sub,on='outcome_label',how='left')
    rows=[]
    for _,r in het_sum.iterrows():
        rows.append([r['het_label'], r['outcome_label'], r['coef_high_group']-r['coef_low_group'], r['interaction_p']])
    for _,r in risk_inter.iterrows():
        rows.append(['Risk exposure', r['outcome_label'], r['coef_high_risk']-r['coef_low_risk'], r['p_interaction']])
    for outcome in ['PCA quality','Execution share','Procurement share']:
        low=low_high[low_high['outcome_label']==outcome].iloc[0]['low_open']
        high=low_high[low_high['outcome_label']==outcome].iloc[0]['high_open']
        p=low_high[low_high['outcome_label']==outcome].iloc[0]['p']
        rows.append(['Gov-data openness', outcome, high-low, p])
    score=pd.DataFrame(rows, columns=['heterogeneity','outcome','gap','p'])
    hets=list(dict.fromkeys(score['heterogeneity']))
    outs=['PCA quality','Execution share','Procurement share']
    fig, ax = plt.subplots(figsize=(10,6))
    ax.set_xlim(0,1); ax.set_ylim(0,1); ax.axis('off')
    left_labels=hets; mid_labels=outs; right_labels=['High-group stronger','Low-group stronger','No clear interaction']
    left_pos={lab:(0.05,0.92-i*0.12) for i,lab in enumerate(left_labels)}
    mid_pos={lab:(0.44,0.80-i*0.25) for i,lab in enumerate(mid_labels)}
    right_pos={lab:(0.82,0.80-i*0.25) for i,lab in enumerate(right_labels)}
    def add_box(x,y,text,fc):
        rect=Rectangle((x,y-0.04),0.13,0.08,facecolor=fc,edgecolor='#333333',lw=1)
        ax.add_patch(rect); ax.text(x+0.065,y,text,ha='center',va='center',fontsize=9)
    for lab,(x,y) in left_pos.items(): add_box(x,y,lab,'#EEF2F6')
    for lab,(x,y) in mid_pos.items(): add_box(x,y,lab,'#F7F7F7')
    for lab,(x,y) in right_pos.items(): add_box(x,y,lab,'#F6F0F0')
    for _,row in score.iterrows():
        l=left_pos[row['heterogeneity']]; m=mid_pos[row['outcome']]
        category='No clear interaction' if row['p']>=0.1 else ('High-group stronger' if row['gap']>0 else 'Low-group stronger')
        r=right_pos[category]
        c=palette['red'] if category=='High-group stronger' else palette['blue'] if category=='Low-group stronger' else '#BFBFBF'
        for (x1,y1),(x2,y2) in [(l,m),(m,r)]:
            arr=FancyArrowPatch((x1+0.13,y1),(x2,y2),arrowstyle='-',lw=1.5 if row['p']<0.1 else 0.8,
                                color=c,alpha=0.7 if row['p']<0.1 else 0.35,connectionstyle='arc3,rad=0.0')
            ax.add_patch(arr)
    ax.set_title('Figure 7-11  Heterogeneity channels and outcome destinations')
    savefig_multi(fig,'Figure_7_11_heterogeneity_flow_summary')

def main():
    het_all, het_sum, risk_comp, risk_inter, risk_all, open_reg = load_data()
    chart1(het_sum); chart2(het_sum); chart3(het_sum); chart4(het_all)
    chart5(risk_comp); chart6(risk_inter); chart7(risk_all); chart8()
    chart9(open_reg); chart10(het_sum, risk_inter, open_reg); chart11(het_sum, risk_inter, open_reg)
    with open(os.path.join(BASE_DIR, 'generation_info.json'),'w',encoding='utf-8') as f:
        json.dump({'charts_generated':11}, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    main()
