# -*- coding: utf-8 -*-
import numpy as np
from konlpy.tag import Twitter
# import csv
import pymysql
twitter = Twitter()
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel, cosine_similarity


#def tokenizer(raw, pos=["Noun", "Alpha", "Verb", "Number"], stopword=[]):
def tokenizer(raw, pos=["Noun", "Alpha", "Verb"], stopword=[]):
  return [
      word for word, tag in twitter.pos(
      raw,
      norm=True,
      stem=True
      )
      if len(word) > 1 and tag in pos and word not in stopword
  ]

def tfidf(search_table,user_id):
    #DB연동
    conn = pymysql.connect(host='localhost', user='root', password='1234', db='posco', charset='utf8')
    curs = conn.cursor(pymysql.cursors.DictCursor)
    #input입력
    #search_table = input("유사도 검사를 진행할 테이블명을 입력해주세요:");
    #db에서 데이터 가져옴
    sql = "select * from "+ search_table
    curs.execute(sql)
    lines = []
    urls = []
    text_companys =[]
    text_headlines = []
    text_sentences = []

    #search_table 안의 데이터 fetch
    rows = curs.fetchall()
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
    #cnt = int(input("인풋의 갯수를 정해주세요:"))

    #TFIDF_keyword 테이블을 만들껀데, 있는경우엔 삭제하고 다시만듬
    sql = "show tables like 'tfidf_"+search_table+"'" #테이블조회
    curs.execute(sql) #조회 실행
    if len(curs.fetchall()) == 1: #테이블이 있는경우 삭제
        sql = "drop table tfidf_"+search_table
        curs.execute(sql)

    sql = "create table tfidf_" + search_table +" ("
    sql += "text_company varchar(20) not null,"
    sql += "text_headline varchar(200) not null,"
    sql += "text_sentence varchar(10000) not null,"
    sql += "addr varchar(1000) not null,"
    sql += "score double(40,5) not null,"
    sql += "ranking integer not null) ENGINE=InnoDB DEFAULT CHARSET=utf8;"
    curs.execute(sql)

    """
    #엑셀에있는거로 처리할때의 코드
    f = open('201907_201907.csv','r')
    rdr = csv.reader(f)
    for line in rdr:
        lines.append(line[1]+line[2])
        urls.append(line[3])
    
    
    f.close()
    """


    vectorize = TfidfVectorizer(
    tokenizer=tokenizer,
    min_df=2,
    sublinear_tf=True
    )



    X = vectorize.fit_transform(lines)
    lines2 = X.toarray()
    features = vectorize.get_feature_names()



    content = []
    content.append('aa')
    cosine_similars = []
    for i in range (0,cnt):
        #content[0] = input("인풋:")
        content[0] = rows[i]['text_headline']+rows[i]['text_sentence']
        srch_vector = vectorize.transform(content)
        cosine_similar = linear_kernel(srch_vector, X).flatten()
        if i==0 :
            cosine_similars = cosine_similar
        else:
            cosine_similars+= cosine_similar

    sim_rank_idx = cosine_similars.argsort()[::-1]

    for i in range(len(sim_rank_idx)-1,0,-1):
        for j in range(0,i):
            if cosine_similars[j] < cosine_similars[j+1]:
                temp_co = cosine_similars[j]
                cosine_similars[j] = cosine_similars[j+1]
                cosine_similars[j+1] = temp_co
                temp_url = urls[j]
                urls[j] = urls[j+1]
                urls[j+1] = temp_url

                temp_company = text_companys[j]
                text_companys[j] = text_companys[j+1]
                text_companys[j+1] = temp_company

                temp_headline = text_headlines[j]
                text_headlines[j] = text_headlines[j+1]
                text_headlines[j+1] = temp_headline

                temp_sentence = text_sentences[j]
                text_sentences[j] = text_sentences[j+1]
                text_sentences[j+1] = temp_sentence

    #tfidf_keyword table에 데이터 추가
    for i in range(0,len(sim_rank_idx)):
        print('{} / score : {} / rank : {} / company : {}'.format(urls[i], cosine_similars[i],i,text_companys[i]))
        sql = "insert into tfidf_" + search_table +" values (%s, %s, %s, %s, %s, %s)"
        curs.execute(sql,(text_companys[i],text_headlines[i],text_sentences[i],urls[i],float(cosine_similars[i]),i))

    conn.commit()
    conn.close()
