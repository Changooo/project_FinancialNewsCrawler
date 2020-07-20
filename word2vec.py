# import csv
import numpy as np
from konlpy.tag import Twitter
from gensim.models import Word2Vec
import pymysql

def tokenizer(raw, pos=["Noun", "Alpha", "Verb"], stopword=[]):
    twitter = Twitter()
    return [
      word for word, tag in twitter.pos(
      raw,
      norm=True,
      stem=True
      )
      if len(word) > 1 and tag in pos and word not in stopword
    ]
def tokenize_document(document):
    # make document to several sentences
    sentences = document.split('다.')
    for i in range(len(sentences)):
        sentences[i] += '다.'

    # tokenize sentences
    tokenized_sentences = []
    for sentence in sentences:
        tokenized_sentence = tokenizer(raw=sentence)
        if len(tokenized_sentence) != 0:
            tokenized_sentences.append(tokenized_sentence)

    #print(tokenized_sentences)
    return tokenized_sentences


def cosine_similarity(vector1, vector2):
    cos = np.dot(vector1, vector2) / (np.linalg.norm(vector1) * np.linalg.norm(vector2))
    if np.isnan(np.sum(cos)):
        return 0
    return cos

def w2v(search_table,user_id):
    conn = pymysql.connect(host='localhost', user='root', password='1234', db='posco', charset='utf8')
    curs = conn.cursor(pymysql.cursors.DictCursor)
    sql = "select * from "+ search_table
    curs.execute(sql)
    lines = []
    urls = []
    text_companys =[]
    text_headlines = []
    text_sentences = []
    rows = curs.fetchall()
    #search_table 안의 데이터 fetch
    for row in rows:
        lines.append(row['text_headline']+row['text_sentence'])
        urls.append(row['addr'])
        text_companys.append(row['text_company'])
        text_headlines.append(row['text_headline'])
        text_sentences.append(row['text_sentence'])
    #input_키워드 table안에 있는 데이터 fetch
    input_keyword = search_table.split('_')[0]
    sql = "select * from input_"+user_id
    curs.execute(sql)
    rows = curs.fetchall()
    cnt = len(rows)
    sql = "show tables like 'w2v_"+search_table+"'" #테이블조회
    curs.execute(sql) #조회 실행
    if len(curs.fetchall()) == 1: #테이블이 있는경우 삭제
        sql = "drop table w2v_"+search_table
        curs.execute(sql)

    sql = "create table w2v_" + search_table +" ("
    sql += "text_company varchar(20) not null,"
    sql += "text_headline varchar(200) not null,"
    sql += "text_sentence varchar(10000) not null,"
    sql += "addr varchar(1000) not null,"
    sql += "score double(40,5) not null,"
    sql += "ranking integer not null)ENGINE=InnoDB DEFAULT CHARSET=utf8;"
    curs.execute(sql)

    """
    # read csv file
    lines = []
    urls = []
    f = open('201907_201907.csv', 'r')
    rdr = csv.reader(f)
    for line in rdr:  # one line = one article (document)
        lines.append(line[2])
        urls.append(line[3])
    f.close()
    """
    # tokenize documents (articles)
    tokenized_documents = []
    tokenized_sentences = []
    for document in lines:
        tokenized_document = tokenize_document(document)
        tokenized_sentences += tokenized_document
        tokenized_documents.append(tokenized_document)
    # learn word2vec model from tokenized documents
    model = Word2Vec(tokenized_sentences, size=300, window=3, min_count=1, workers=1, iter=100)
    word_vectors = model.wv

    # document to vec (final result: vectorized_documents (list) - elements: each vector contains vector of each document)
    vectorized_documents = []
    for document in tokenized_documents:
        document_vec = []
        for sentence in document:
            word_vecs = []
            for word in sentence:
                try:
                    vec = word_vectors[word]
                    word_vecs.append(vec)
                except KeyError:
                    pass

            sentence_vecs = np.mean(word_vecs, axis=0)  # 한 문장에 대한 vector
            document_vec.append(sentence_vecs)

        # print(len(document_vec))
        # print(np.mean(document_vec, axis=0))
        vectorized_documents.append(np.mean(document_vec, axis=0))


    cosine_similars = []
    for i in range(0,cnt):
        content = rows[i]['text_headline']+rows[i]['text_sentence']
        tokenized_search_article = tokenize_document(content)
        vectorized_serach_sentences = []
        for sentence in tokenized_search_article:
            word_vecs = []
            for word in sentence:
                try:
                    vec = word_vectors[word]
                    word_vecs.append(vec)
                except KeyError:
                    pass

            sentence_vecs = np.mean(word_vecs, axis=0)
            vectorized_serach_sentences.append(sentence_vecs)

        vectorized_search_article = np.mean(vectorized_serach_sentences, axis=0)

        # similarity (vecotrized_search_article vs. vectorized_documents)
        similarity = []
        for document in vectorized_documents:
            cos = cosine_similarity(vectorized_search_article, document)
            similarity.append(cos)
        if i == 0 :
            cosine_similars = similarity
        else:
            for si in range(0,len(similarity)):
                cosine_similars[si] += similarity[si]
    rank_idx = np.array(cosine_similars).argsort()[::-1]
    #w2v_keyword table에 데이터 추가
    rank = 0
    for i in rank_idx:
        print('{} / score : {} / rank : {} / company : {}'.format(urls[i], cosine_similars[i],rank,text_companys[i]))
        sql = "insert into w2v_" + search_table +" values (%s, %s, %s, %s, %s, %s)"
        curs.execute(sql,(text_companys[i],text_headlines[i],text_sentences[i],urls[i],float(cosine_similars[i]),rank))
        rank+=1
    conn.commit()
    conn.close()


