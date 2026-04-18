
import pandas as pd, re, numpy as np

DATA_XLSX = "数据总表.xlsx"
DICT_XLSX = "PPP_Word2Vec扩词结果_V2_四级十二类_实际执行版.xlsx"
TOPIC_XLSX = "PPP_BERTopic正式版_V2_四级十二类_实际执行版.xlsx"

def clean_text(text):
    if pd.isna(text):
        return ""
    t = str(text)
    t = re.sub(r'【法宝引证码】.*?(?:\n|$)', '', t)
    t = re.sub(r'原文链接[:：].*?(?:\n|$)', '', t)
    t = t.replace('\r', '\n')
    t = re.sub(r'\n{2,}', '\n', t)
    return t.strip()

def extract_folder_name(s):
    s = str(s)
    s = re.sub(r'[\(（].*?[\)）]', '', s)
    s = re.sub(r'\d+', '', s)
    return s.strip().replace(' ', '')

def norm_province(s):
    s = str(s)
    s = s.replace('省','').replace('市','').replace('壮族自治区','').replace('回族自治区','').replace('维吾尔自治区','').replace('自治区','').replace('特别行政区','').strip()
    return s

def extract_year_from_path(p):
    m = re.search(r'(20\d{2})年', str(p))
    return int(m.group(1)) if m else np.nan

df = pd.read_excel(DATA_XLSX, sheet_name='政府与社会资本合作_txt文本整合结果')
df['clean_text'] = df['文件内容'].apply(clean_text)
df['province'] = df['一级子文件夹'].apply(extract_folder_name).apply(norm_province)

ber = pd.read_excel(TOPIC_XLSX, sheet_name='文档主题分配')
topic_total = pd.read_excel(TOPIC_XLSX, sheet_name='主题总表')
topic_map = topic_total[['主题编号','主题名称','主维度','主题标签']].rename(columns={'主题编号':'topic'})

df = df.merge(ber[['相对路径','year','topic']], on='相对路径', how='left')
df['year'] = df['year'].fillna(df['相对路径'].apply(extract_year_from_path))
df = df.merge(topic_map, on='topic', how='left')

dict2 = pd.read_excel(DICT_XLSX, sheet_name='合并后词典V2建议版')
dict2['词项'] = dict2['词项'].astype(str).str.strip()
dict2 = dict2[dict2['词项']!=''].drop_duplicates(subset=['二级代码','词项'])
phrases_by_code = dict2.groupby('二级代码')['词项'].apply(list).to_dict()

df['char_len'] = df['clean_text'].str.replace(r'\s+','',regex=True).str.len()
df['sentence_count'] = df['clean_text'].str.count(r'[。；！？!?；]') + 1

codes = list(phrases_by_code)
for code, phrases in phrases_by_code.items():
    df[f'{code}_cnt'] = [sum(text.count(p) for p in phrases) for text in df['clean_text']]
    df[f'{code}_bin'] = (df[f'{code}_cnt'] > 0).astype(int)
    df[f'{code}_idx'] = df[f'{code}_cnt'] / df['char_len'].replace(0,np.nan) * 10000

for prefix in ['A','B','C']:
    code_cols = [f'{c}_cnt' for c in codes if c.startswith(prefix)]
    df[f'{prefix}_cnt'] = df[code_cols].sum(axis=1)
    df[f'{prefix}_idx'] = df[f'{prefix}_cnt'] / df['char_len'].replace(0,np.nan) * 10000

for col in ['A_idx','B_idx','C_idx']:
    df[f'z_{col}'] = (df[col]-df[col].mean())/df[col].std(ddof=0)
df['ppp_governance_capacity_index'] = df[['z_A_idx','z_B_idx','z_C_idx']].mean(axis=1)
df['ppp_norm_risk_index'] = df[['z_B_idx','z_C_idx']].mean(axis=1)

doc_cols = ['序号','一级子文件夹','province','相对路径','文件名','year','topic','主题名称','主维度','主题标签',
            'char_len','sentence_count'] + [f'{c}_cnt' for c in codes] + [f'{c}_idx' for c in codes] + \
           ['A_cnt','A_idx','B_cnt','B_idx','C_cnt','C_idx','ppp_governance_capacity_index','ppp_norm_risk_index']
df[doc_cols].to_csv('PPP_doc_level_variables_v2_四级十二类_实际执行版.csv', index=False, encoding='utf-8-sig')
