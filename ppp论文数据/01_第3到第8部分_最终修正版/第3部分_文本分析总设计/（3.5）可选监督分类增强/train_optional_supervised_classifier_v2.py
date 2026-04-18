
import pandas as pd, numpy as np, re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.multiclass import OneVsRestClassifier
from sklearn.svm import LinearSVC
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score, precision_score, recall_score, accuracy_score
from sklearn.preprocessing import OneHotEncoder
from scipy.sparse import hstack, csr_matrix

label_cols=['A1','A2','B1','B2','B3','B4','C1','C2','C3']

def clean_text(s):
    s=str(s)
    s=re.sub(r'【法宝引证码】.*?\n','',s)
    s=re.sub(r'原文链接：https?://\S+','',s)
    s=re.sub(r'\s+',' ',s)
    return s.strip()

text_df = pd.read_excel('/mnt/data/数据总表.xlsx', sheet_name='政府与社会资本合作_txt文本整合结果', usecols=[0,3,4])
text_df.columns=['id','file_name','raw_text']
text_df['text'] = text_df['raw_text'].map(clean_text)

score = pd.read_excel('/mnt/data/PPP_V2正式试编码结果.xlsx', sheet_name='120篇文档评分矩阵')
docvars = pd.read_csv('/mnt/data/PPP_doc_level_variables_v2_四级十二类_实际执行版.csv')

df = score.merge(text_df[['id','file_name','text']], left_on='序号', right_on='id', how='left').merge(
    docvars[['序号','topic','A1_idx','A2_idx','B1_idx','B2_idx','B3_idx','B4_idx','C1_idx','C2_idx','C3_idx']], on='序号', how='left'
)

Y = (df[label_cols] >= 2).astype(int).values
texts = df['text'].fillna('').str.slice(0,1500).tolist()
X_train_txt, X_test_txt, y_train, y_test, idx_train, idx_test = train_test_split(
    texts, Y, np.arange(len(texts)), test_size=0.2, random_state=42
)

vec = TfidfVectorizer(analyzer='char', ngram_range=(2,4), max_features=8000, min_df=1)
Xtr = vec.fit_transform(X_train_txt)
Xte = vec.transform(X_test_txt)

aux_numeric = df[[c+'_idx' for c in label_cols]].fillna(0.0).values
enc = OneHotEncoder(handle_unknown='ignore', sparse_output=True)
topic_sparse = enc.fit_transform(df[['topic']].fillna(-1))
aux_sparse = hstack([csr_matrix(aux_numeric), topic_sparse])

Xtr_h = hstack([Xtr, aux_sparse[idx_train]])
Xte_h = hstack([Xte, aux_sparse[idx_test]])

models = {
    'TFIDF+NB': (OneVsRestClassifier(MultinomialNB()), Xtr, Xte),
    'TFIDF+LinearSVC': (OneVsRestClassifier(LinearSVC()), Xtr, Xte),
    'Hybrid+LinearSVC': (OneVsRestClassifier(LinearSVC()), Xtr_h, Xte_h),
}

rows=[]
for name,(clf,AA,BB) in models.items():
    clf.fit(AA, y_train)
    pred = clf.predict(BB)
    rows.append({
        'model': name,
        'micro_f1': f1_score(y_test, pred, average='micro', zero_division=0),
        'macro_f1': f1_score(y_test, pred, average='macro', zero_division=0),
        'micro_precision': precision_score(y_test, pred, average='micro', zero_division=0),
        'micro_recall': recall_score(y_test, pred, average='micro', zero_division=0),
        'subset_accuracy': accuracy_score(y_test, pred),
    })
result = pd.DataFrame(rows).sort_values('micro_f1', ascending=False)
print(result)

best = OneVsRestClassifier(LinearSVC())
X_train_full = vec.fit_transform(df['text'].fillna('').str.slice(0,1500))
best.fit(X_train_full, Y)
text_df['text_trunc'] = text_df['text'].fillna('').str.slice(0,1500)
X_all = vec.transform(text_df['text_trunc'])
pred_all = best.predict(X_all)
auto = pd.DataFrame(pred_all, columns=[c+'_pred' for c in label_cols])
auto.insert(0,'id', text_df['id'].values)
auto.insert(1,'file_name', text_df['file_name'].values)
auto.to_csv('/mnt/data/PPP_supervised_autocoding_v2_四级十二类_实际执行版.csv', index=False, encoding='utf-8-sig')
