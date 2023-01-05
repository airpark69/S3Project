import os
from sklearn.linear_model import SGDClassifier
from gensim.models.fasttext import FastText
from sklearn.feature_extraction.text import CountVectorizer
import hgtk
import pandas as pd
import numpy as np
from tqdm import tqdm
from konlpy.tag import Okt
import time
import pickle
import joblib
import datetime
from app.functions import database
from app.functions.db_models import CORPUS


#######  init 과정에서 모델 미리 로드해놓기
embedding_path = os.path.dirname(os.path.realpath(__file__)) + "/MLmodels/fastText_40.joblib"
filename = os.path.dirname(os.path.realpath(__file__)) + "/MLmodels/svm_40_alpha00001_log.pickle"
ft_num_features = 40

### 여기서 모델을 로드할 경우, import 할때마다 모델이 로드된다.
### 따라서 __init__ 으로 옮기고, 받아오는 식으로 한다.

starttime = time.time()
ft_model = joblib.load(embedding_path)
loaded_model = pickle.load(open(filename, "rb"))
okt = Okt()
endtime = time.time()
ela_time = endtime - starttime
print("경과 시간 : ", ela_time)
print("!!!!!!!! 모델이 로드 되었습니다 !!!!!!!!")
#######

def tokenize_by_jamo(s):
    return [word_to_jamo(token) for token in okt.morphs(s)]

# 글자를 자모단위로 분해
def word_to_jamo(token):
    def to_special_token(jamo):
      if not jamo:
        return '-'
      else:
        return jamo
    decomposed_token = ''

    for char in token:
        try:
        # char( 음 절 ) 을 초 성 , 중 성 , 종 성 으 로 분 리
            cho, jung, jong = hgtk.letter.decompose(char)

            # 자 모 가 빈 문 자 일 경 우 특 수 문 자 - 로 대 체
            cho = to_special_token(cho)
            jung = to_special_token(jung)
            jong = to_special_token(jong)
            decomposed_token = decomposed_token + cho + jung + jong

        # 만 약 char( 음 절 ) 이 한 글 이 아 닐 경 우 자 모 를 나 누 지 않 고 추 가
        except Exception as exception:
            if type(exception).__name__ == 'NotHangulException':
                decomposed_token += char

    # 단 어 토 큰 의 자 모 단 위 분 리 결 과 를 추 가
    return decomposed_token

# 자모 단위를 글자로 결합
def jamo_to_word(jamo_sequence):
    tokenized_jamo = []
    index = 0

    while index < len(jamo_sequence):
    # 문 자 가 한 글 ( 정 상 적 인 자 모 ) 이 아 닐 경 우
        if not hgtk.checker.is_hangul(jamo_sequence[index]):
            tokenized_jamo.append(jamo_sequence[index])
            index = index + 1

    # 문 자 가 정 상 적 인 자 모 라 면 초 성 , 중 성 , 종 성 을 하 나 의 토 큰 으 로 간 주 .
        else:
            tokenized_jamo.append(jamo_sequence[index:index + 3])
            index = index + 3

        word = ''
        try:
            for jamo in tokenized_jamo:
            # 초 성 , 중 성 , 종 성 의 묶 음 으 로 추 정 되 는 경 우
                if len(jamo) == 3:
                    if jamo[2] == "-":
                    # 종 성 이 존 재 하 지 않 는 경 우
                        word = word + hgtk.letter.compose(jamo[0], jamo[1])
                    else:
                # 종 성 이 존 재 하 는 경 우
                        word = word + hgtk.letter.compose(jamo[0], jamo[1], jamo[2])
                # 한 글 이 아 닌 경 우
                else:
                    word = word + jamo

            # 복 원 중 (hgtk.letter.compose) 에 러 발 생 시 초 기 입 력 리 턴 .
            # 복 원 이 불 가 능 한 경 우 예 시 ) ' ﾤ ! ﾱ ﾧ ￌ ﾷ ﾵ ￃ ﾷ '
        except Exception as exception:
            if type(exception).__name__ == 'NotHangulException':
                return jamo_sequence

    return word

# 입력값 최종 전처리
def document_vectorizer(corpus, model, num_features):
    vocabulary = set(model.wv.index_to_key)
    
    def average_word_vectors(words, model, vocabulary, num_features):
        feature_vector = np.zeros((num_features,), dtype="float64")
        nwords = 0.
        
        for word in words:
            if word in vocabulary: 
                nwords = nwords + 1.
                feature_vector = np.add(feature_vector, model.wv[word])
        if nwords:
            feature_vector = np.divide(feature_vector, nwords)

        return feature_vector

    features = [average_word_vectors(tokenized_sentence, model, vocabulary, num_features)
                    for tokenized_sentence in tqdm(corpus)]
    return np.array(features)

def tokenized(data):
  tokenized_data=[]

  for sample in tqdm(data):
      tokenzied_sample = tokenize_by_jamo(sample) # 자 소 단 위 토 큰 화
      tokenized_data.append(tokenzied_sample)

  return tokenized_data

def levenshtein(s1, s2, cost=None, debug=False):
    if len(s1) < len(s2):
        return levenshtein(s2, s1, debug=debug)

    if len(s2) == 0:
        return len(s1)

    if cost is None:
        cost = {}

    # changed
    def substitution_cost(c1, c2):
        if c1 == c2:
            return 0
        return cost.get((c1, c2), 1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            # Changed
            substitutions = previous_row[j] + substitution_cost(c1, c2)
            current_row.append(min(insertions, deletions, substitutions))

        if debug:
            print(current_row[1:])

        previous_row = current_row

    return previous_row[-1]

def Get_Category(menu):
    predict_feature = document_vectorizer(corpus=tokenized([menu]), model=ft_model, num_features=ft_num_features)
    predicted = loaded_model.predict(predict_feature)

    return predicted[0]

def Get_origin_score(menu):
    decomposed_menu = word_to_jamo(menu)
    predicted = Get_Category(decomposed_menu)

    decomposed_pred = word_to_jamo(predicted)
    leven_score = levenshtein(decomposed_pred, decomposed_menu) / 3

    origin_score = (len(decomposed_menu) - leven_score) / len(decomposed_menu) * 100

    return origin_score


def get_tfidf_max(corpus, target):
    if len(corpus) == 0:
        return 0
    vect = CountVectorizer()
    document_term_matrix = vect.fit_transform(corpus)       # 문서-단어 행렬 

    tf = pd.DataFrame(document_term_matrix.toarray(), columns=vect.get_feature_names_out())  
                                                # TF (Term Frequency)
    D = len(tf)
    df = tf.astype(bool).sum(axis=0)
    idf = np.log((D+1) / (df+1)) + 1             # IDF (Inverse Document Frequency)

    # TF-IDF (Term Frequency-Inverse Document Frequency)
    tfidf = tf * idf                      
    tfidf = tfidf / np.linalg.norm(tfidf, axis=1, keepdims=True)

    target_col =[]

    for col in tfidf.columns:
        if target in col:
            target_col.append(col)

    print(target_col)

    try:
        max_tfidf = tfidf[target_col].max().max()
    except:
        max_tfidf = 0
    
    print(max_tfidf)

    if np.isnan(max_tfidf) :
        max_tfidf = 0

    return max_tfidf

def Get_trend_score(menu):
    decomposed_menu = word_to_jamo(menu)
    pred_category = Get_Category(decomposed_menu)

    corpus = []
    #dt_now = datetime.datetime.now().date() - datetime.timedelta(days=1)
    dt_now = datetime.datetime.now().date()
    data_list = database.get_by_category_time(CORPUS, pred_category, dt_now)

    ## 값이 없으면 최근 태그가 없다는 이야기므로 트랜드성 0
    if data_list.count() == 0:
        return 0

    for data in data_list:
        corpus.append(data.text)

    return get_tfidf_max(corpus, menu) * 100


def Get_all_score_json(menu):
    predicted = Get_Category(menu)
    origin_score = Get_origin_score(menu)
    trend_score = Get_trend_score(menu)
    dt_now = datetime.datetime.now()
    
    data_dict = {'pred_category':predicted, 'origin_score':round(origin_score, 2), 'trend_score':round(trend_score,2),\
                 'use_time':dt_now}

    return data_dict
    

    