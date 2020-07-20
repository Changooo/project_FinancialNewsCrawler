from konlpy.tag import Twitter
import pymysql

def key_similarity(search_table,user_id):
    t = Twitter()
    #db 연동
    conn = pymysql.connect(host='localhost', user='root', password='1234', db='posco', charset='utf8')
    curs = conn.cursor(pymysql.cursors.DictCursor)
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

    #keywords_키워드 table 데이터 fetch
    sql = "select * from keywords_" +user_id
    curs.execute(sql)
    rows = curs.fetchall()
    key_list =[]
    key_check =[]
    for row in rows:
        key_list.append(row['keyword'])
        key_check.append(0)

    #keyword_키워드 테이블을 만들껀데, 이미 있는 경우 삭제
    sql = "show tables like 'keyword_" + search_table +"'"      #table 조회
    curs.execute(sql)
    if len(curs.fetchall()) == 1:                               #table이 있는 경우 삭제
        sql = "drop table keyword_" + search_table
        curs.execute(sql)

    sql = "create table keyword_" + search_table +" ("
    sql += "text_company varchar(20) not null,"
    sql += "text_headline varchar(200) not null,"
    sql += "text_sentence varchar(10000) not null,"
    sql += "addr varchar(1000) not null,"
    sql += "score double(40,5) not null,"
    sql += "idx int auto_increment primary key ) ENGINE=InnoDB DEFAULT CHARSET=utf8;"
    curs.execute(sql)


    for i in range(0,len(lines)):
        tags = t.pos(lines[i])
        sco = 0.0
        for j in range(0,len(key_check)):
            key_check[j] = 0
        for tag in tags:
            # 명사, 영어, 동사가 아닐 경우 키워드 유사도 검사를 진행하지 않음
            if not (tag[1] == "Noun" or tag[1] == "Alpha" or tag[1] == "Verb"):
                continue

            # key_list의 단어와 일치하는 경우 유사도 검사
            for j in range(0,len(key_list)):
                if tag[0] == key_list[j]:
                    sco += pow(0.1,key_check[j])
                    key_check[j]+=1
        for key in key_check:
            key = 0

        #keyword_키워드 table에 데이터 추가
        sql = "insert into keyword_" + search_table +" (text_company,text_headline,text_sentence,addr,score) values (%s, %s, %s, %s, %s)"
        curs.execute(sql,(text_companys[i],text_headlines[i],text_sentences[i],urls[i],sco))

    conn.commit()
    conn.close()


