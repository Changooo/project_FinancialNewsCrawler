from flask import Flask, render_template, Response,request,session
from flask_bootstrap import Bootstrap
#import navercrawling
#import navercrawling2
import navercrawling3
import googlecrawling
import pymysql
import TFIDF
import word2vec
import keyword_similarity
import mailing
from textrankr import TextRank

#testasdfhh
app = Flask(__name__)
#Flask 생성자
app.secret_key = "super secret key"
Bootstrap(app)
#TEST SENTENCE


#처음에 Local Host에 접속할 때 어떤 화면이 나오고 어떤 기능을 하는지 설명
@app.route('/')
def index():
#Login 상태에 들어가있지 않은 상황이면 /login.html로 넘어가게 된다
    if not session.get('login'):
        return render_template('/login.html')
    user_root = False
#Root 계정으로 접속했을 경우 일어나는 상황입니다.
    if session.get('root'):
        user_root = True
    conn = pymysql.connect(host='localhost', user='root', password='1234', db='posco', charset='UTF8MB4')
    curs = conn.cursor()
#MySQL 접속이 성공하면, Connection 객체로부터 cursor() 메서드를 호출하여 Cursor 객체를 가져옴
    sql = "show tables from posco where tables_in_posco not like 'user' and tables_in_posco not like 'input_%' and tables_in_posco not like 'tfidf_%' and tables_in_posco not like 'w2v_%' and tables_in_posco not like 'keyword%' and tables_in_posco not like 'reserve_' and tables_in_posco not like 'signup' and tables_in_posco not like 'user'"
    curs.execute(sql)
#Cursor 객체의 execute() 메서드를 사용하여 SQL 문장을 DB 서버에 전송
    rows = curs.fetchall()
#커서의 fetchall() 메서드는 모든 데이타를 한꺼번에 클라이언트로 가져올 때 사용된다.
    keyword =[]
    page_count = []
    year = []
    month = []
    day = []
    time = []
    TF_check = []
    W2V_check = []
    for row in rows:
        sql = "show tables from posco where tables_in_posco like 'tfidf_" + str(row)[2:-3] + "'"
        curs.execute(sql)
        if len(curs.fetchall()) == 1:
            TF_check.append(True)
        else:
            TF_check.append(False)

        sql = "show tables from posco where tables_in_posco like 'w2v_" + str(row)[2:-3] + "'"
        curs.execute(sql)
        if len(curs.fetchall()) == 1:
            W2V_check.append(True)
        else:
            W2V_check.append(False)

        splitdata = str(row).split('_')
        keyword.append(splitdata[0][2:])
        page_count.append(splitdata[1])
        year.append(splitdata[2][0:4])
        month.append(splitdata[2][4:6])
        day.append(splitdata[2][6:8])
        time.append(splitdata[2][8:12])
    conn.close()
    length = len(keyword)
#/index.html로 넘어가서 keyword,page_count,year,month,day,time,TF_check,W2V_check, lenth를 index.html파일에 맞춰서 웹 페이지에 보이게 한다.
    return render_template('/index.html',keyword=keyword,page_count=page_count,year=year,month=month,day=day,time=time,TF_check=TF_check,W2V_check=W2V_check,length=length,user_root=user_root)

#기사 수집에 필요한 정보를 얻는 과정
@app.route('/collect.html')
def collect():
    if not session.get('login'):
        return render_template('/login.html')
    user_root = False
    if session.get('root'):
        user_root = True
    return render_template('/collect.html',user_root=user_root)

@app.route('/crawling', methods=['POST','GET'])
#검색을 누르게 되면 Crawling Part로 넘어가게 될 것이다. 이제 crawling함수를 받아오게 된다.
def crawling():
    if not session.get('login'):
        return render_template('/login.html')
    user_root = False
    if session.get('root'):
        user_root = True
#우리가 time,volume,site,search에 입력한 값을 받아와서 각 변수에 저장
    time = request.form['time']
    volume = (request.form['volume'])
    site = request.form['site']
    search = (request.form['search'])
#사이트가 Naver이면  navercrawling3 파일에 있는 함수를 이용
    if site=="naver":
        #navercrawling.navercl(volume,search)
        navercrawling3.navercl3(volume,search,time)
        #navercrawling_multi.navercl3(volume,search,time)
#사이트가 Google이면  googlecrawling 파일에 있는 함수를 이용
    elif site=="google":
        googlecrawling.googlecl2(volume,search,time)
    conn = pymysql.connect(host='localhost', user='root', password='1234', db='posco', charset='UTF8MB4')
    curs = conn.cursor()
    sql = "show tables from posco where tables_in_posco not like 'user' and tables_in_posco not like 'input_%' and tables_in_posco not like 'tfidf_%' and tables_in_posco not like 'w2v_%' and tables_in_posco not like 'keyword%' and tables_in_posco not like 'reserve_' and tables_in_posco not like 'signup' and tables_in_posco not like 'user'"
    curs.execute(sql)
    rows = curs.fetchall()
    keyword =[]
    page_count = []
    year = []
    month = []
    day = []
    time = []
    TF_check = []
    W2V_check = []
    for row in rows:
        sql = "show tables from posco where tables_in_posco like 'tfidf_" + str(row)[2:-3] + "'"
        curs.execute(sql)
        if len(curs.fetchall()) == 1:
            TF_check.append(True)
        else:
            TF_check.append(False)

        sql = "show tables from posco where tables_in_posco like 'w2v_" + str(row)[2:-3] + "'"
        curs.execute(sql)
        if len(curs.fetchall()) == 1:
            W2V_check.append(True)
        else:
            W2V_check.append(False)

        splitdata = str(row).split('_')
        keyword.append(splitdata[0][2:])
        page_count.append(splitdata[1])
        year.append(splitdata[2][0:4])
        month.append(splitdata[2][4:6])
        day.append(splitdata[2][6:8])
        time.append(splitdata[2][8:12])
    conn.close()
    length = len(keyword)
    return render_template('/index.html',keyword=keyword,page_count=page_count,year=year,month=month,day=day,time=time,TF_check=TF_check,W2V_check=W2V_check,length=length,user_root=user_root)
#크롤링 2번째 파트에 넘어갈 때 사용 되는 부분
@app.route('/crawling2', methods=['POST','GET'])
def crawling2():
    if not session.get('login'):
        return render_template('/login.html')
    user_root = False
    if session.get('root'):
        user_root = True
    time = request.form['time']
    volume = (request.form['volume'])
    site = request.form['site']
    search = (request.form['search'])
    rank = int(request.form['rank'])
    email = (request.form['email'])
    similarity = (request.form['similarity'])
    splitdata = str(search).split(',')
    text_companys = []
    text_headlines = []
    addrs = []
    for search in splitdata:
        tableName = ""
        if site=="naver":
            tableName = navercrawling3.navercl3(volume,search,time)
        elif site=="google":
            tableName = googlecrawling.googlecl2(volume,search,time)

        similarTable = ""
        if similarity == 'keyword':
            keyword_similarity.key_similarity(tableName,session['user_id'])
            similarTable = 'keyword_'
        elif similarity == 'TFIDF':
            TFIDF.tfidf(tableName,session['user_id'])
            similarTable = 'tfidf_'
        elif similarity == 'word2vec':
            word2vec.w2v(tableName,session['user_id'])
            similarTable = 'w2v_'
        similarTable += tableName

        conn = pymysql.connect(host='localhost', user='root', password='1234', db='posco', charset='UTF8MB4')
        curs = conn.cursor(pymysql.cursors.DictCursor)
        sql = "select * from "+ similarTable +" order by score desc"
        curs.execute(sql)
        rows = curs.fetchall()

        i=0
        for row in rows:
            if i == rank:
                break
            text_companys.append(row['text_company'])
            text_headlines.append(row['text_headline'])
            addrs.append(row['addr'])
            i+=1
        conn.close()
    length = len(text_companys)
    contents = ""
    for i in range(0,length):
        if i % rank == 0 :
            contents += splitdata[int(i/rank)] + '\n'
        #print(text_companys[i] + "/" + text_headlines[i] + "/" +addrs[i] )
        contents += text_companys[i] + "/" + text_headlines[i] + "/" +addrs[i] + "\n"
    print(contents)
    mailing.mailing(tableName,contents,email)
    return render_template('/collect.html',user_root=user_root)

#TF-IDF나 W2V 검사 버튼을 눌렀을 때 실행 되는 부분
@app.route('/check.html')
def tables():
    if not session.get('login'):
        return render_template('/login.html')
    user_root = False
    if session.get('root'):
        user_root = True
    conn = pymysql.connect(host='localhost', user='root', password='1234', db='posco', charset='UTF8MB4')
    curs = conn.cursor()
    sql = "show tables from posco where tables_in_posco not like 'user' and tables_in_posco not like 'input_%' and tables_in_posco not like 'tfidf_%' and tables_in_posco not like 'w2v_%' and tables_in_posco not like 'keyword%' and tables_in_posco not like 'reserve_' and tables_in_posco not like 'signup' and tables_in_posco not like 'user'"
    curs.execute(sql)
    rows = curs.fetchall()
    keyword =[]
    page_count = []
    year = []
    month = []
    day = []
    time = []
    TF_check = []
    W2V_check = []
    KEY_check = []
    for row in rows:
        sql = "show tables from posco where tables_in_posco like 'tfidf_" + str(row)[2:-3] + "'"
        curs.execute(sql)
        if len(curs.fetchall()) == 1:
            TF_check.append(True)
        else:
            TF_check.append(False)

        sql = "show tables from posco where tables_in_posco like 'w2v_" + str(row)[2:-3] + "'"
        curs.execute(sql)
        if len(curs.fetchall()) == 1:
            W2V_check.append(True)
        else:
            W2V_check.append(False)

        sql = "show tables from posco where tables_in_posco like 'keyword_" + str(row)[2:-3] + "'"
        curs.execute(sql)
        if len(curs.fetchall()) == 1:
            KEY_check.append(True)
        else:
            KEY_check.append(False)

        splitdata = str(row).split('_')
        keyword.append(splitdata[0][2:])
        page_count.append(splitdata[1])
        year.append(splitdata[2][0:4])
        month.append(splitdata[2][4:6])
        day.append(splitdata[2][6:8])
        time.append(splitdata[2][8:12])
    conn.close()
    length = len(keyword)
    return render_template('/check.html',keyword=keyword,page_count=page_count,year=year,month=month,day=day,time=time,TF_check=TF_check,W2V_check=W2V_check,KEY_check = KEY_check,length=length,user_root=user_root)

#TF-IDF검사 과정
@app.route('/check/TFIDF/<tableName>', methods=['GET'])
def de_TFIDF(tableName):
    if not session.get('login'):
        return render_template('/login.html')
    user_root = False
    if session.get('root'):
        user_root = True
    TFIDF.tfidf(tableName,session['user_id'])
    conn = pymysql.connect(host='localhost', user='root', password='1234', db='posco', charset='UTF8MB4')
    curs = conn.cursor()
    sql = "show tables from posco where tables_in_posco not like 'user' and tables_in_posco not like 'input_%' and tables_in_posco not like 'tfidf_%' and tables_in_posco not like 'w2v_%' and tables_in_posco not like 'keyword%' and tables_in_posco not like 'reserve_' and tables_in_posco not like 'signup' and tables_in_posco not like 'user'"
    curs.execute(sql)
    rows = curs.fetchall()
    keyword =[]
    page_count = []
    year = []
    month = []
    day = []
    time = []
    TF_check = []
    W2V_check = []
    KEY_check =[]
    for row in rows:
        sql = "show tables from posco where tables_in_posco like 'tfidf_" + str(row)[2:-3] + "'"
        curs.execute(sql)
        if len(curs.fetchall()) == 1:
            TF_check.append(True)
        else:
            TF_check.append(False)

        sql = "show tables from posco where tables_in_posco like 'w2v_" + str(row)[2:-3] + "'"
        curs.execute(sql)
        if len(curs.fetchall()) == 1:
            W2V_check.append(True)
        else:
            W2V_check.append(False)

        sql = "show tables from posco where tables_in_posco like 'keyword_" + str(row)[2:-3] + "'"
        curs.execute(sql)
        if len(curs.fetchall()) == 1:
            KEY_check.append(True)
        else:
            KEY_check.append(False)

        splitdata = str(row).split('_')
        keyword.append(splitdata[0][2:])
        page_count.append(splitdata[1])
        year.append(splitdata[2][0:4])
        month.append(splitdata[2][4:6])
        day.append(splitdata[2][6:8])
        time.append(splitdata[2][8:12])
    conn.close()
    length = len(keyword)
    return render_template('/check.html',keyword=keyword,page_count=page_count,year=year,month=month,day=day,time=time,TF_check=TF_check,W2V_check=W2V_check,KEY_check=KEY_check,length=length,user_root=user_root)
#W2V검사 과정
@app.route('/check/W2V/<tableName>', methods=['GET'])
def de_W2V(tableName):
    if not session.get('login'):
        return render_template('/login.html')
    user_root = False
    if session.get('root'):
        user_root = True
    word2vec.w2v(tableName,session['user_id'])
    conn = pymysql.connect(host='localhost', user='root', password='1234', db='posco', charset='UTF8MB4')
    curs = conn.cursor()
    sql = "show tables from posco where tables_in_posco not like 'user' and tables_in_posco not like 'input_%' and tables_in_posco not like 'tfidf_%' and tables_in_posco not like 'w2v_%' and tables_in_posco not like 'keyword%' and tables_in_posco not like 'reserve_' and tables_in_posco not like 'signup' and tables_in_posco not like 'user'"
    curs.execute(sql)
    rows = curs.fetchall()
    keyword =[]
    page_count = []
    year = []
    month = []
    day = []
    time = []
    TF_check = []
    W2V_check = []
    KEY_check = []
    for row in rows:
        sql = "show tables from posco where tables_in_posco like 'tfidf_" + str(row)[2:-3] + "'"
        curs.execute(sql)
        if len(curs.fetchall()) == 1:
            TF_check.append(True)
        else:
            TF_check.append(False)

        sql = "show tables from posco where tables_in_posco like 'w2v_" + str(row)[2:-3] + "'"
        curs.execute(sql)
        if len(curs.fetchall()) == 1:
            W2V_check.append(True)
        else:
            W2V_check.append(False)

        sql = "show tables from posco where tables_in_posco like 'keyword_" + str(row)[2:-3] + "'"
        curs.execute(sql)
        if len(curs.fetchall()) == 1:
            KEY_check.append(True)
        else:
            KEY_check.append(False)

        splitdata = str(row).split('_')
        keyword.append(splitdata[0][2:])
        page_count.append(splitdata[1])
        year.append(splitdata[2][0:4])
        month.append(splitdata[2][4:6])
        day.append(splitdata[2][6:8])
        time.append(splitdata[2][8:12])
    conn.close()
    length = len(keyword)
    return render_template('/check.html',keyword=keyword,page_count=page_count,year=year,month=month,day=day,time=time,TF_check=TF_check,W2V_check=W2V_check,KEY_check = KEY_check,length=length,user_root=user_root)

#지정해둔 키워드와 검색된 기사가 얼마나 유사한지를 보여주는 과정
@app.route('/check/key_similarity/<tableName>', methods=['GET'])
def key_similarity(tableName):
    if not session.get('login'):
        return render_template('/login.html')
    user_root = False
    if session.get('root'):
        user_root = True
    keyword_similarity.key_similarity(tableName,session['user_id'])
    conn = pymysql.connect(host='localhost', user='root', password='1234', db='posco', charset='UTF8MB4')
    curs = conn.cursor()
    sql = "show tables from posco where tables_in_posco not like 'user' and tables_in_posco not like 'input_%' and tables_in_posco not like 'tfidf_%' and tables_in_posco not like 'w2v_%' and tables_in_posco not like 'keyword%' and tables_in_posco not like 'reserve_' and tables_in_posco not like 'signup' and tables_in_posco not like 'user'"
    curs.execute(sql)
    rows = curs.fetchall()
    keyword =[]
    page_count = []
    year = []
    month = []
    day = []
    time = []
    TF_check = []
    W2V_check = []
    KEY_check = []
    for row in rows:
        sql = "show tables from posco where tables_in_posco like 'tfidf_" + str(row)[2:-3] + "'"
        curs.execute(sql)
        if len(curs.fetchall()) == 1:
            TF_check.append(True)
        else:
            TF_check.append(False)

        sql = "show tables from posco where tables_in_posco like 'w2v_" + str(row)[2:-3] + "'"
        curs.execute(sql)
        if len(curs.fetchall()) == 1:
            W2V_check.append(True)
        else:
            W2V_check.append(False)

        sql = "show tables from posco where tables_in_posco like 'keyword_" + str(row)[2:-3] + "'"
        curs.execute(sql)
        if len(curs.fetchall()) == 1:
            KEY_check.append(True)
        else:
            KEY_check.append(False)

        splitdata = str(row).split('_')
        keyword.append(splitdata[0][2:])
        page_count.append(splitdata[1])
        year.append(splitdata[2][0:4])
        month.append(splitdata[2][4:6])
        day.append(splitdata[2][6:8])
        time.append(splitdata[2][8:12])
    conn.close()
    length = len(keyword)
    return render_template('/check.html',keyword=keyword,page_count=page_count,year=year,month=month,day=day,time=time,TF_check=TF_check,W2V_check=W2V_check,KEY_check=KEY_check,length=length,user_root=user_root)


#지정해둔 기사와 검색된 기사가 얼마나 유사한지를 보여주는 과정
@app.route('/check/similarity/<tableName>', methods=['GET'])
def similarity(tableName):
    if not session.get('login'):
        return render_template('/login.html')
    user_root = False
    if session.get('root'):
        user_root = True
    conn = pymysql.connect(host='localhost', user='root', password='1234', db='posco', charset='UTF8MB4')
    curs = conn.cursor(pymysql.cursors.DictCursor)
    sql = "select * from "+ tableName
    curs.execute(sql)
    rows = curs.fetchall()
    rankings = []
    scores = []
    text_companys = []
    text_headlines = []
    addrs = []
    for row in rows:
        rankings.append(row['ranking'])
        scores.append(row['score'])
        text_companys.append(row['text_company'])
        text_headlines.append(row['text_headline'])
        addrs.append(row['addr'])
    conn.close()
    length = len(text_companys)
    return render_template('similarity.html',text_companys=text_companys,text_headlines=text_headlines,addrs=addrs,rankings=rankings,scores=scores,length=length,tableName=tableName,user_root=user_root)

#지정해둔 키워드와 얼마나 유사한지 체크해주는 과정
@app.route('/check/key_similarity_check/<tableName>', methods=['GET'])
def key_similarity_check(tableName):
    if not session.get('login'):
        return render_template('/login.html')
    user_root = False
    if session.get('root'):
        user_root = True
    conn = pymysql.connect(host='localhost', user='root', password='1234', db='posco', charset='UTF8MB4')
    curs = conn.cursor(pymysql.cursors.DictCursor)
    sql = "select * from "+ tableName +" order by score desc"
    curs.execute(sql)
    rows = curs.fetchall()
    rankings = []
    scores = []
    text_companys = []
    text_headlines = []
    addrs = []
    idxs = []
    i=0
    for row in rows:
        idxs.append(row['idx'])
        rankings.append(str(i))
        scores.append(row['score'])
        text_companys.append(row['text_company'])
        text_headlines.append(row['text_headline'])
        addrs.append(row['addr'])
        i+=1

    conn.close()
    length = len(text_companys)
    return render_template('similarity.html',text_companys=text_companys,text_headlines=text_headlines,addrs=addrs,rankings=rankings,scores=scores,length=length,tableName=tableName,idxs=idxs,user_root=user_root)

#유사도 검사 이후 등수를 보여주는 코드
@app.route('/check/similarity/<tableName>/<ranking>', methods=['GET'])
def similarity2(tableName,ranking):
    if not session.get('login'):
        return render_template('/login.html')
    user_root = False
    if session.get('root'):
        user_root = True
    searchName = str(tableName).split('_')[1]
    conn = pymysql.connect(host='localhost', user='root', password='1234', db='posco', charset='UTF8MB4')
    curs = conn.cursor()
    sql = "show tables like 'input_" + session['user_id'] + "'"
    curs.execute(sql)
    if len(curs.fetchall()) == 0:
        sql = "create table input_"+session['user_id'] +" ("
        sql += "text_company varchar(20) not null,"
        sql += "text_headline varchar(200) not null,"
        sql += "text_sentence varchar(10000) not null,"
        sql += "addr varchar(1000) not null,"
        sql += "idx int auto_increment primary key ) ENGINE=InnoDB DEFAULT CHARSET=utf8;"
        curs.execute(sql)
    curs = conn.cursor(pymysql.cursors.DictCursor)
    if tableName[0] == 'k':
        sql = "select * from "+ tableName + " where idx=" + ranking
    else:
        sql = "select * from "+ tableName + " where ranking=" + ranking
    curs.execute(sql)
    rows = curs.fetchall()
    for row in rows:
        sql = "insert into input_"+session['user_id'] +" (text_company,text_headline,text_sentence,addr) values (%s,%s,%s,%s)"
        curs.execute(sql, (row['text_company'],row['text_headline'],row['text_sentence'],row['addr']))
    conn.commit()
    sql = "select * from "+ tableName
    curs.execute(sql)
    rows = curs.fetchall()
    rankings = []
    scores = []
    text_companys = []
    text_headlines = []
    addrs = []
    idxs = []
    i = 0
    for row in rows:
        if tableName[0] == 'k':
            rankings.append(str(i))
            idxs.append(row['idx'])
        else:
            rankings.append(row['ranking'])
        scores.append(row['score'])
        text_companys.append(row['text_company'])
        text_headlines.append(row['text_headline'])
        addrs.append(row['addr'])
        i+= 1
    conn.close()
    length = len(text_companys)
    return render_template('similarity.html',text_companys=text_companys,text_headlines=text_headlines,addrs=addrs,rankings=rankings,scores=scores,length=length,tableName=tableName,idxs=idxs,user_root=user_root)

#기사의 제목, 회사,주소, 등 여러가지 정보를 처리하는 과정
@app.route('/check/insideData.html/<tableName>', methods=['GET'])
def inside(tableName):
    if not session.get('login'):
        return render_template('/login.html')
    user_root = False
    if session.get('root'):
        user_root = True
    conn = pymysql.connect(host='localhost', user='root', password='1234', db='posco', charset='UTF8MB4')
    curs = conn.cursor(pymysql.cursors.DictCursor)
    sql = "select * from "+ tableName
    curs.execute(sql)
    rows = curs.fetchall()
    text_companys = []
    text_headlines = []
    addrs = []
    idxs = []
    for row in rows:
        idxs.append(row['idx'])
        text_companys.append(row['text_company'])
        text_headlines.append(row['text_headline'])
        addrs.append(row['addr'])
    conn.close()
    length = len(text_companys)
    return render_template('insideData.html',text_companys=text_companys,text_headlines=text_headlines,addrs=addrs,idxs=idxs,length=length,tableName=tableName,user_root=user_root)

#크롤링해서 가져온 정보들을 가지고 요약을 진행하는 과정
@app.route('/check/insideData.html/summary/<tableName>/<index>', methods=['GET'])
def summary(tableName,index):
    if not session.get('login'):
        return render_template('/login.html')
    user_root = False
    if session.get('root'):
        user_root = True
    conn = pymysql.connect(host='localhost', user='root', password='1234', db='posco', charset='UTF8MB4')
    curs = conn.cursor(pymysql.cursors.DictCursor)
    sql = "select * from "+ tableName + " where idx=" + index
    curs.execute(sql)
    rows = curs.fetchall()
    text_companys = ""
    text_headlines = ""
    addrs = ""
    summ_text_sentence = ""
    summ_3_text_sentence =""
    for row in rows:
        textrank = TextRank(row['text_sentence'])
        addrs = row['addr']
        text_companys = row['text_company']
        text_headlines = row['text_headline']
        summ_text_sentence = str(textrank.summarize())
        summ_3_text_sentence = textrank.summarize(3,verbose=False)

    return render_template('summary.html',text_companys=text_companys,text_headlines=text_headlines,addrs=addrs,tableName=tableName,summ_text_sentence=summ_text_sentence,summ_3_text_sentence=summ_3_text_sentence,user_root=user_root)

#table에 저장되어있던 정보들을 삭제하는 과정
@app.route('/check/delete/<tableName>', methods=['GET'])
def delete(tableName):
    if not session.get('login'):
        return render_template('/login.html')
    user_root = False
    if session.get('root'):
        user_root = True
    conn = pymysql.connect(host='localhost', user='root', password='1234', db='posco', charset='UTF8MB4')
    curs = conn.cursor(pymysql.cursors.DictCursor)
    sql = "drop table " + tableName
    curs.execute(sql)

    sql = "show tables from posco where tables_in_posco like 'keyword_"+tableName+"'"
    curs.execute(sql)
    if len(curs.fetchall()) != 0:
        sql = "drop table keyword_" + tableName
        curs.execute(sql)

    sql = "show tables from posco where tables_in_posco like 'tfidf_"+tableName+"'"
    curs.execute(sql)
    if len(curs.fetchall()) != 0:
        sql = "drop table tfidf_" + tableName
        curs.execute(sql)

    sql = "show tables from posco where tables_in_posco like 'w2v_"+tableName+"'"
    curs.execute(sql)
    if len(curs.fetchall()) != 0:
        sql = "drop table w2v_" + tableName
        curs.execute(sql)

    sql = "show tables from posco where tables_in_posco not like 'user' and tables_in_posco not like 'input_%' and tables_in_posco not like 'tfidf_%' and tables_in_posco not like 'w2v_%' and tables_in_posco not like 'keyword%' and tables_in_posco not like 'reserve_' and tables_in_posco not like 'signup' and tables_in_posco not like 'user'"
    curs.execute(sql)
    rows = curs.fetchall()
    keyword =[]
    page_count = []
    year = []
    month = []
    day = []
    time = []
    TF_check = []
    W2V_check = []
    KEY_check = []
    for row in rows:
        sql = "show tables from posco where tables_in_posco like 'tfidf_" + str(row['Tables_in_posco']) + "'"
        curs.execute(sql)
        if len(curs.fetchall()) == 1:
            TF_check.append(True)
        else:
            TF_check.append(False)

        sql = "show tables from posco where tables_in_posco like 'w2v_" + str(row['Tables_in_posco']) + "'"
        curs.execute(sql)
        if len(curs.fetchall()) == 1:
            W2V_check.append(True)
        else:
            W2V_check.append(False)

        sql = "show tables from posco where tables_in_posco like 'keyword_" + str(row['Tables_in_posco']) + "'"
        curs.execute(sql)
        if len(curs.fetchall()) == 1:
            KEY_check.append(True)
        else:
            KEY_check.append(False)


        splitdata = str(row['Tables_in_posco']).split('_')
        keyword.append(splitdata[0])
        page_count.append(splitdata[1])
        year.append(splitdata[2][0:4])
        month.append(splitdata[2][4:6])
        day.append(splitdata[2][6:8])
        time.append(splitdata[2][8:12])
    conn.close()
    length = len(keyword)
    return render_template('/check.html',keyword=keyword,page_count=page_count,year=year,month=month,day=day,time=time,TF_check=TF_check,W2V_check=W2V_check,KEY_check = KEY_check,length=length,user_root=user_root)

#키워드를 눌렀을 때 그 키워드로 검색된 기사들의 내용을 보여주는 과정
@app.route('/check/insideData.html/<tableName>/<index>', methods=['GET'])
def inside2(tableName,index):
    if not session.get('login'):
        return render_template('/login.html')
    user_root = False
    if session.get('root'):
        user_root = True
    searchName = str(tableName).split('_')[0]
    conn = pymysql.connect(host='localhost', user='root', password='1234', db='posco', charset='UTF8MB4')
    curs = conn.cursor()
    sql = "show tables like 'input_"+ session['user_id'] +"'"
    curs.execute(sql)
    if len(curs.fetchall()) == 0:
        sql = "create table input_"+session['user_id']+" ("
        sql += "text_company varchar(20) not null,"
        sql += "text_headline varchar(200) not null,"
        sql += "text_sentence varchar(10000) not null,"
        sql += "addr varchar(1000) not null,"
        sql += "idx int auto_increment primary key ) ENGINE=InnoDB DEFAULT CHARSET=utf8;"
        curs.execute(sql)
    curs = conn.cursor(pymysql.cursors.DictCursor)
    sql = "select * from "+ tableName + " where idx=" + index
    curs.execute(sql)
    rows = curs.fetchall()
    for row in rows:
        sql = "insert into input_"+session['user_id'] + "(text_company,text_headline,text_sentence,addr) values (%s,%s,%s,%s)"
        curs.execute(sql, (row['text_company'],row['text_headline'],row['text_sentence'],row['addr']))
    conn.commit()
    sql = "select * from "+ tableName
    curs.execute(sql)
    rows = curs.fetchall()
    text_companys = []
    text_headlines = []
    addrs = []
    idxs = []
    for row in rows:
        idxs.append(row['idx'])
        text_companys.append(row['text_company'])
        text_headlines.append(row['text_headline'])
        addrs.append(row['addr'])
    conn.close()
    length = len(text_companys)
    return render_template('insideData.html',text_companys=text_companys,text_headlines=text_headlines,addrs=addrs,idxs=idxs,length=length,tableName=tableName,user_root=user_root)

#관심 기사를 등록하는 과정
@app.route('/input.html')
def input():
    if not session.get('login'):
        return render_template('/login.html')
    user_root = False
    if session.get('root'):
        user_root = True
    conn = pymysql.connect(host='localhost', user='root', password='1234', db='posco', charset='UTF8MB4')
    curs = conn.cursor()
    sql = "show tables from posco where tables_in_posco like 'input_%'"
    curs.execute(sql)
    rows = curs.fetchall()
    keyword =[]
    lens = []
    user_ids = []
    curs = conn.cursor(pymysql.cursors.DictCursor)
    for row in rows:
        key = str(row).split('_')[1][:-3]
        if key == session['user_id']:
            user_ids.append(True)
        else:
            user_ids.append(False)
        sql = "select count(*) from input_" + key
        curs.execute(sql)
        lens.append(curs.fetchall()[0]['count(*)'])
        keyword.append(key)

    conn.close()
    length = len(keyword)
    return render_template('/input.html',keyword=keyword,lens=lens,length=length,user_root=user_root,user_ids = user_ids)

# 계정별 관심기사 show ( params: 계정 ID )
@app.route('/input/input_insideData/<tablename>', methods=['GET'])
def input_insideData(tablename):
    # 세션 check
    if not session.get('login'):
        return render_template('/login.html')
    user_root = False
    if session.get('root'):
        user_root = True

    conn = pymysql.connect(host='localhost', user='root', password='1234', db='posco', charset='UTF8MB4')
    curs = conn.cursor(pymysql.cursors.DictCursor)
    # 계정별 관심기사 data 참조
    sql = "select * from input_" + tablename
    curs.execute(sql)
    rows = curs.fetchall()
    text_companys = []
    text_headlines = []
    addrs = []
    idxs = []
    for row in rows:
        text_companys.append(row['text_company'])
        text_headlines.append(row['text_headline'])
        addrs.append(row['addr'])
        idxs.append(row['idx'])
    conn.close()
    length = len(text_companys)

    # 계정별 관심기사 page 이동
    return render_template('input_insideData.html',text_companys=text_companys,text_headlines=text_headlines,addrs=addrs,length=length,idxs=idxs,user_root=user_root)

# 계정별 관심기사 삭제 ( params: 계정ID )
@app.route('/input/delete/<tableName>')
def input_delete(tableName):
    # 세션 check
    if not session.get('login'):
        return render_template('/login.html')
    user_root = False
    if session.get('root'):
        user_root = True

    conn = pymysql.connect(host='localhost', user='root', password='1234', db='posco', charset='UTF8MB4')
    curs = conn.cursor(pymysql.cursors.DictCursor)
    # 계정별 관심기사 삭제
    sql = "drop table " + tableName
    curs.execute(sql)

    conn = pymysql.connect(host='localhost', user='root', password='1234', db='posco', charset='UTF8MB4')
    curs = conn.cursor()
    # props 넘겨주기 위한 관심기사 data 참조
    sql = "show tables from posco where tables_in_posco like 'input_%'"
    curs.execute(sql)
    rows = curs.fetchall()
    keyword =[]
    lens = []
    user_ids = []
    curs = conn.cursor(pymysql.cursors.DictCursor)
    for row in rows:
        key = str(row).split('_')[1][:-3]
        if key == session['user_id']:
            user_ids.append(True)
        else:
            user_ids.append(False)
        sql = "select count(*) from input_" + key
        curs.execute(sql)
        lens.append(curs.fetchall()[0]['count(*)'])
        keyword.append(key)

    conn.close()
    length = len(keyword)

    # 관심기사 page 이동
    return render_template('/input.html',keyword=keyword,lens=lens,length=length,user_root=user_root,user_ids = user_ids)

# 관심기사 id별 삭제 ( params: 관심기사 id )
@app.route('/input/input_insideData/delete/<idx>', methods=['GET'])
def input_insideData_delete(idx):
    # 세션 check
    if not session.get('login'):
        return render_template('/login.html')
    user_root = False
    if session.get('root'):
        user_root = True

    conn = pymysql.connect(host='localhost', user='root', password='1234', db='posco', charset='UTF8MB4')
    curs = conn.cursor(pymysql.cursors.DictCursor)
    # 관심기사 id별 삭제
    sql = "delete from input_"+session['user_id'] +" where idx='" + str(idx) +"'"
    curs.execute(sql)
    conn.commit()

    # props 넘겨주기 위한 계정별 관심기사 data 참조
    sql = "select * from input_" + session['user_id']
    curs.execute(sql)
    rows = curs.fetchall()
    text_companys = []
    text_headlines = []
    addrs = []
    idxs=[]
    for row in rows:
        text_companys.append(row['text_company'])
        text_headlines.append(row['text_headline'])
        addrs.append(row['addr'])
        idxs.append(row['idx'])
    conn.close()
    length = len(text_companys)

    # 계정별 관심기사 page 이동
    return render_template('input_insideData.html',text_companys=text_companys,text_headlines=text_headlines,addrs=addrs,length=length,idxs=idxs,user_root=user_root)

# 수집예약 page show
@app.route('/reserve.html',methods=['GET'])
def reserve():
    # 세션 check
    if not session.get('login'):
        return render_template('/login.html')
    user_root = False
    if session.get('root'):
        user_root = True

    # 수집예약 page 이동
    return render_template('reserve.html',user_root=user_root)

# 수집예약 data 저장
@app.route('/reservation', methods=['POST','GET'])
def reservation():
    # 세션 check
    if not session.get('login'):
        return render_template('/login.html')
    user_root = False
    if session.get('root'):
        user_root = True

    # props 가져오기
    time = request.form['time']
    volume = (request.form['volume'])
    site = request.form['site']
    search = (request.form['search'])
    rank = int(request.form['rank'])
    email = (request.form['email'])
    similarity = (request.form['similarity'])
    hour = request.form['hour']
    minute = request.form['minute']

    conn = pymysql.connect(host='localhost', user='root', password='1234', db='posco', charset='UTF8MB4')
    curs = conn.cursor()
    sql = "show tables like 'reserve_'"
    curs.execute(sql)
    # 데이터 없을 시 수집예약 테이블 새로 생성
    if len(curs.fetchall()) == 0:
        sql = "create table reserve_ ("
        sql += "time varchar(10) not null,"
        sql += "volume varchar(10) not null,"
        sql += "site varchar(100) not null,"
        sql += "search varchar(1000) not null,"
        sql += "ranking varchar(10) not null,"
        sql += "email varchar(50) not null,"
        sql += "similarity varchar(10) not null,"
        sql += "hour varchar(10) not null,"
        sql += "minute varchar(10) not null,"
        sql += "userid varchar(30) not null,"
        sql += "idx int auto_increment primary key ) ENGINE=InnoDB DEFAULT CHARSET=utf8;"
        curs.execute(sql)
    curs = conn.cursor(pymysql.cursors.DictCursor)
    sql = "insert into reserve_ (time,volume,site,search,ranking,email,similarity,hour,minute,userid) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    curs.execute(sql, (time,volume,site,search,rank,email,similarity,hour,minute,session['user_id']))
    conn.commit()

    # 수집예약 page 이동
    return render_template('/reserve.html',user_root=user_root)

# 예약확인 page show
@app.route('/reserve_check.html',methods=['GET'])
def reserve_check():
    # 세션 check
    if not session.get('login'):
        return render_template('/login.html')
    user_root = False
    if session.get('root'):
        user_root = True

    conn = pymysql.connect(host='localhost', user='root', password='1234', db='posco', charset='UTF8MB4')
    curs = conn.cursor()
    sql = "show tables like 'reserve_'"
    curs.execute(sql)
    # 데이터없을 시 수집예약 테이블 생성
    if len(curs.fetchall()) == 0:
        sql = "create table reserve_ ("
        sql += "time varchar(10) not null,"
        sql += "volume varchar(10) not null,"
        sql += "site varchar(100) not null,"
        sql += "search varchar(1000) not null,"
        sql += "ranking varchar(10) not null,"
        sql += "email varchar(50) not null,"
        sql += "similarity varchar(10) not null,"
        sql += "hour varchar(10) not null,"
        sql += "minute varchar(10) not null,"
        sql += "userid varchar(30) not null,"
        sql += "idx int auto_increment primary key ) ENGINE=InnoDB DEFAULT CHARSET=utf8; "
        curs.execute(sql)
    curs = conn.cursor(pymysql.cursors.DictCursor)
    sql = "select * from reserve_"
    curs.execute(sql)

    # props 넘겨주기 위한 수집예약 data 참조
    rows = curs.fetchall()
    times = []
    volumes = []
    sites = []
    searchs = []
    rankings = []
    emails = []
    similaritys = []
    hours = []
    minutes = []
    idxs = []
    userids = []
    for row in rows:
        times.append(row['time'])
        volumes.append(row['volume'])
        sites.append(row['site'])
        searchs.append(row['search'])
        rankings.append(row['ranking'])
        emails.append(row['email'])
        similaritys.append(row['similarity'])
        hours.append(row['hour'])
        minutes.append(row['minute'])
        userids.append(row['userid'])
        idxs.append(row['idx'])
    conn.close()
    length = len(times)

    # 예약확인 page 이동
    return render_template('/reserve_check.html',times = times,volumes=volumes,sites=sites,searchs=searchs,rankings=rankings,emails=emails,similaritys=similaritys,hours=hours,minutes=minutes,length=length,idxs=idxs,user_root=user_root,userids=userids)

# 수집예약 id별 삭제 (param: 수집예약 id)
@app.route('/reserve_delete/<idx>',methods=['GET'])
def reserve_delete(idx):
    # 세션 check
    if not session.get('login'):
        return render_template('/login.html')
    user_root = False
    if session.get('root'):
        user_root = True

    conn = pymysql.connect(host='localhost', user='root', password='1234', db='posco', charset='UTF8MB4')
    curs = conn.cursor(pymysql.cursors.DictCursor)
    # 수집예약 id별 삭제
    sql = "delete from reserve_ where idx='" +str(idx) +"'"
    curs.execute(sql)
    conn.commit()

    # props 넘겨주기 위한 수집예약 data 참조
    sql = "select * from reserve_"
    curs.execute(sql)
    rows = curs.fetchall()
    times = []
    volumes = []
    sites = []
    searchs = []
    rankings = []
    emails = []
    similaritys = []
    hours = []
    minutes = []
    idxs = []
    userids = []
    for row in rows:
        times.append(row['time'])
        volumes.append(row['volume'])
        sites.append(row['site'])
        searchs.append(row['search'])
        rankings.append(row['ranking'])
        emails.append(row['email'])
        similaritys.append(row['similarity'])
        hours.append(row['hour'])
        minutes.append(row['minute'])
        userids.append(row['userid'])
        idxs.append(row['idx'])
    conn.close()
    length = len(times)

    # 예약확인 page 이동
    return render_template('/reserve_check.html',times = times,volumes=volumes,sites=sites,searchs=searchs,rankings=rankings,emails=emails,similaritys=similaritys,hours=hours,minutes=minutes,length=length,idxs=idxs,user_root=user_root,userids=userids)

# 로그인 page show
@app.route('/login.html', methods=['POST','GET'])
def login_page():
    # 세션 check
    user_root = False
    if session.get('root'):
        user_root = True

    # 로그인 page 이동
    return render_template('/login.html',user_root=user_root)

# 로그인 rest, 세션 등록
@app.route('/login', methods=['POST','GET'])
def login():
    id = request.form['userid']
    pw = request.form['userpw']

    conn = pymysql.connect(host='localhost', user='root', password='1234', db='posco', charset='UTF8MB4')
    curs = conn.cursor(pymysql.cursors.DictCursor)
    sql = "show tables like 'user'"
    curs.execute(sql)

    # 데이터 없을 시 user 테이블 생성
    if len(curs.fetchall()) == 0:
        sql = "create table user ("
        sql += "firstname varchar(20) not null,"
        sql += "lastname varchar(20) not null,"
        sql += "userid varchar(30) primary key,"
        sql += "userpw varchar(50) not null )  ENGINE=InnoDB DEFAULT CHARSET=utf8;"
        curs.execute(sql)

    if id == 'root' and pw == 'posco1234!':
        # root계정 로그인
        session['login'] = True
        session['root'] = True
        session['user_id'] = 'root'
    else:
        # 일반계정 로그인
        conn = pymysql.connect(host='localhost', user='root', password='1234', db='posco', charset='UTF8MB4')
        curs = conn.cursor()
        sql = "select * from user where userid='" + id + "' and userpw='" + pw+"'"
        curs.execute(sql)
        rows = curs.fetchall()
        if len(rows) != 0:
            session['login'] = True
            for row in rows:
                session['user_id'] = row[2]

        conn.close()


    # root 세션 등록
    user_root = False
    if session.get('root'):
        user_root = True

    #print(session.get('login'))
    if session.get('login'):
        #성공 시 main page이동
        return render_template('/collect.html',user_root=user_root)
    else :
        #실패 시 로그인 page이동
        return render_template('/login.html',user_root=user_root)

# 회원가입 page show
@app.route('/register.html' )
def signup():
    user_root = False
    if session.get('root'):
        user_root = True
    return render_template('/register.html',user_root=user_root)

# 회원가입 rest
@app.route('/register', methods=['POST','GET'])
def register():
    user_root = False
    if session.get('root'):
        user_root = True
    firstname = request.form['firstName']
    lastname = request.form['lastName']
    userid = request.form['userid']
    userpw = request.form['userpw']

    conn = pymysql.connect(host='localhost', user='root', password='1234', db='posco', charset='UTF8MB4')
    curs = conn.cursor()
    sql = "show tables like 'signup'"
    curs.execute(sql)
    #데이터 없을 시 user 테이블 생성
    if len(curs.fetchall()) == 0:
        sql = "create table signup ("
        sql += "firstname varchar(20) not null,"
        sql += "lastname varchar(20) not null,"
        sql += "userid varchar(30) primary key,"
        sql += "userpw varchar(50) not null ) ENGINE=InnoDB DEFAULT CHARSET=utf8;"
        curs.execute(sql)

    #회원가입 정보 insert
    curs = conn.cursor(pymysql.cursors.DictCursor)
    sql = "insert into signup (firstname,lastname,userid,userpw) values (%s,%s,%s,%s)"
    curs.execute(sql, (firstname,lastname,userid,userpw))
    conn.commit()

    return render_template('/login.html',user_root=user_root)

# 로그아웃 rest, 세션 초기화
@app.route('/logout')
def logout():
    session['login'] = False
    session['root'] = False
    session['user_id'] = None

    return render_template('/login.html')

# 가입승인 page show
@app.route('/signup_list.html')
def signup_list():
    user_root = False
    if session.get('root'):
        user_root = True
    # admin 권한 check
    if user_root == False:
        pass        # 접근 제한 필요

    conn = pymysql.connect(host='localhost', user='root', password='1234', db='posco', charset='UTF8MB4')
    curs = conn.cursor(pymysql.cursors.DictCursor)
    # props 넘겨주기위한 가입목록 data 참조
    sql = "select * from signup"
    curs.execute(sql)
    rows = curs.fetchall()
    firstnames = []
    lastnames = []
    userids = []
    userpws = []
    for row in rows:
        firstnames.append(row['firstname'])
        lastnames.append(row['lastname'])
        userids.append(row['userid'])
        userpws.append(row['userpw'])
    length = len(userids)
    conn.close()
    return render_template('/signup_list.html',firstnames=firstnames,lastnames=lastnames,userids=userids,userpws=userpws,length=length,user_root=user_root)

# 가입 허가 rest (params: userId)
@app.route('/signup_list/ok/<userid>')
def signup_okay(userid):
    user_root = False
    if session.get('root'):
        user_root = True
    # admin 권한 check
    if user_root == False:
        pass        # 접근 제한 필요

    conn = pymysql.connect(host='localhost', user='root', password='1234', db='posco', charset='UTF8MB4')
    curs = conn.cursor()
    sql = "show tables like 'user'"
    curs.execute(sql)
    # 데이터 없을 시 user 테이블 생성
    if len(curs.fetchall()) == 0:
        sql = "create table user ("
        sql += "firstname varchar(20) not null,"
        sql += "lastname varchar(20) not null,"
        sql += "userid varchar(30) primary key,"
        sql += "userpw varchar(50) not null ) ENGINE=InnoDB DEFAULT CHARSET=utf8;"
        curs.execute(sql)
    curs = conn.cursor(pymysql.cursors.DictCursor)
    sql = "select * from signup where userid='"+userid + "'"
    curs.execute(sql)

    # 가입목록 DB에 존재하는 USER -> user DB로 insert
    rows = curs.fetchall()
    firstname = ""
    lastname = ""
    userpw = ""
    for row in rows:
        firstname = (row['firstname'])
        lastname = (row['lastname'])
        userid = (row['userid'])
        userpw = (row['userpw'])
    sql = "insert into user (firstname,lastname,userid,userpw) values (%s,%s,%s,%s)"
    curs.execute(sql, (firstname,lastname,userid,userpw))
    conn.commit()

    # 가입목록 DB에 존재하는 USER 삭제
    sql = "delete from signup where userid='" +userid +"'"
    curs.execute(sql)
    conn.commit()

    # props 넘겨주기 위한 가입목록 data 참조
    conn = pymysql.connect(host='localhost', user='root', password='1234', db='posco', charset='UTF8MB4')
    curs = conn.cursor(pymysql.cursors.DictCursor)
    sql = "select * from signup"
    curs.execute(sql)
    rows = curs.fetchall()
    firstnames = []
    lastnames = []
    userids = []
    userpws = []
    for row in rows:
        firstnames.append(row['firstname'])
        lastnames.append(row['lastname'])
        userids.append(row['userid'])
        userpws.append(row['userpw'])
    length = len(userids)
    conn.close()
    return render_template('/signup_list.html',firstnames=firstnames,lastnames=lastnames,userids=userids,userpws=userpws,length=length,user_root=user_root)

# 가입 거절 rest (params: userId)
@app.route('/signup_list/cancel/<userid>')
def signup_cancel(userid):
    user_root = False
    if session.get('root'):
        user_root = True
    if user_root == False:
        pass        # 접근 제한 필요
    conn = pymysql.connect(host='localhost', user='root', password='1234', db='posco', charset='UTF8MB4')
    curs = conn.cursor(pymysql.cursors.DictCursor)

    # 가입목록 DB에 존재하는 USER 삭제
    sql = "delete from signup where userid='" +userid +"'"
    curs.execute(sql)
    conn.commit()

    # props 넘겨주기 위한 가입목록 data 참조
    sql = "select * from signup"
    curs.execute(sql)
    rows = curs.fetchall()
    firstnames = []
    lastnames = []
    userids = []
    userpws = []
    for row in rows:
        firstnames.append(row['firstname'])
        lastnames.append(row['lastname'])
        userids.append(row['userid'])
        userpws.append(row['userpw'])
    length = len(userids)
    conn.close()
    return render_template('/signup_list.html',firstnames=firstnames,lastnames=lastnames,userids=userids,userpws=userpws,length=length,user_root=user_root)

# user목록 page show
@app.route('/user_list.html')
def user_list():
    user_root = False
    if session.get('root'):
        user_root = True
    # admin 권한 check
    if user_root == False:
        pass  # 접근 제한 필요

    # props 넘겨주기 위한 user data 참조
    conn = pymysql.connect(host='localhost', user='root', password='1234', db='posco', charset='UTF8MB4')
    curs = conn.cursor(pymysql.cursors.DictCursor)
    sql = "select * from user"
    curs.execute(sql)
    rows = curs.fetchall()
    firstnames = []
    lastnames = []
    userids = []
    userpws = []
    for row in rows:
        firstnames.append(row['firstname'])
        lastnames.append(row['lastname'])
        userids.append(row['userid'])
        userpws.append(row['userpw'])
    length = len(userids)
    conn.close()
    return render_template('/user_list.html',firstnames=firstnames,lastnames=lastnames,userids=userids,userpws=userpws,length=length,user_root=user_root)

# 회원 박탈 rest (params: userId)
@app.route('/user_list/cancel/<userid>')
def user_delete(userid):
    user_root = False
    if session.get('root'):
        user_root = True
    # admin 권한 check
    if user_root == False:
        pass  # 접근 제한 필요

    conn = pymysql.connect(host='localhost', user='root', password='1234', db='posco', charset='UTF8MB4')
    curs = conn.cursor(pymysql.cursors.DictCursor)
    # user DB 에서 회원 삭제
    sql = "delete from user where userid='" +userid +"'"
    curs.execute(sql)
    conn.commit()

    # props 넘겨주기 위한 user data 참조
    sql = "select * from user"
    curs.execute(sql)
    rows = curs.fetchall()
    firstnames = []
    lastnames = []
    userids = []
    userpws = []
    for row in rows:
        firstnames.append(row['firstname'])
        lastnames.append(row['lastname'])
        userids.append(row['userid'])
        userpws.append(row['userpw'])
    length = len(userids)
    conn.close()
    return render_template('/user_list.html',firstnames=firstnames,lastnames=lastnames,userids=userids,userpws=userpws,length=length,user_root=user_root)

# 키워드 기반 검사 - 키워드 리스트 목록 page show
@app.route('/check/key_list.html')
def key_list():
    if not session.get('login'):
        return render_template('/login.html')
    user_root = False
    if session.get('root'):
        user_root = True

    conn = pymysql.connect(host='localhost', user='root', password='1234', db='posco', charset='UTF8MB4')
    curs = conn.cursor()
    # props 넘겨주기 위한 키워드 리스트 data 목록 참조
    sql = "show tables from posco where tables_in_posco like 'keywords_%'"
    curs.execute(sql)
    rows = curs.fetchall()
    keyword =[]
    lens = []
    user_ids = []
    curs = conn.cursor(pymysql.cursors.DictCursor)
    for row in rows:
        # 세션에 있는 user의 키워드 리스트가 무엇인지 user_ids에 기억
        key = str(row).split('_')[1][:-3]
        if key == session['user_id']:
            user_ids.append(True)
        else:
            user_ids.append(False)
        sql = "select count(*) from keywords_" + key
        curs.execute(sql)
        lens.append(curs.fetchall()[0]['count(*)'])
        keyword.append(key)

    conn.close()
    length = len(keyword)
    return render_template('/key_list.html',keyword=keyword,lens=lens,length=length,user_root=user_root,user_ids = user_ids)

# 키워드 리스트 추가 rest
@app.route('/check/key_list/add')
def key_list_add():
    if not session.get('login'):
        return render_template('/login.html')
    user_root = False
    if session.get('root'):
        user_root = True

    conn = pymysql.connect(host='localhost', user='root', password='1234', db='posco', charset='UTF8MB4')
    curs = conn.cursor()
    sql = "show tables like 'keywords_" + session['user_id']+"'"
    curs.execute(sql)
    # data 없으면 키워드 테이블 생성
    if len(curs.fetchall()) == 0:
        sql = "create table keywords_"+ session['user_id'] + " ("
        sql += "keyword varchar(50) not null,"
        sql += "idx int auto_increment primary key) ENGINE=InnoDB DEFAULT CHARSET=utf8;"
        curs.execute(sql)

    conn = pymysql.connect(host='localhost', user='root', password='1234', db='posco', charset='UTF8MB4')
    curs = conn.cursor()
    # props 넘겨주기 위한 키워드 리스트 목록 data 참조
    sql = "show tables from posco where tables_in_posco like 'keywords_%'"
    curs.execute(sql)
    rows = curs.fetchall()
    keyword =[]
    lens = []
    user_ids = []
    curs = conn.cursor(pymysql.cursors.DictCursor)
    for row in rows:
        # 세션에 있는 user의 키워드 리스트가 무엇인지 user_ids에 기억
        key = str(row).split('_')[1][:-3]
        if key == session['user_id']:
            user_ids.append(True)
        else:
            user_ids.append(False)
        sql = "select count(*) from keywords_" + key
        curs.execute(sql)
        lens.append(curs.fetchall()[0]['count(*)'])
        keyword.append(key)

    conn.close()
    length = len(keyword)
    return render_template('/key_list.html',keyword=keyword,lens=lens,length=length,user_root=user_root,user_ids = user_ids)

# 키워드 리스트 삭제 rest
@app.route('/check/key_list/delete/<tableName>')
def key_list_delete(tableName):
    if not session.get('login'):
        return render_template('/login.html')
    user_root = False
    if session.get('root'):
        user_root = True

    conn = pymysql.connect(host='localhost', user='root', password='1234', db='posco', charset='UTF8MB4')
    curs = conn.cursor(pymysql.cursors.DictCursor)
    # 키워드 리스트 삭제
    sql = "drop table " + tableName
    curs.execute(sql)
    curs = conn.cursor()

    # props 넘겨주기 위한 키워드 리스트 목록 data 참조
    sql = "show tables from posco where tables_in_posco like 'keywords_%'"
    curs.execute(sql)
    rows = curs.fetchall()
    keyword =[]
    lens = []
    user_ids = []
    curs = conn.cursor(pymysql.cursors.DictCursor)
    for row in rows:
        # 세션에 있는 user의 키워드 리스트가 무엇인지 user_ids에 기억
        key = str(row).split('_')[1][:-3]
        if key == session['user_id']:
            user_ids.append(True)
        else:
            user_ids.append(False)
        sql = "select count(*) from keywords_" + key
        curs.execute(sql)
        lens.append(curs.fetchall()[0]['count(*)'])
        keyword.append(key)

    conn.close()
    length = len(keyword)
    return render_template('/key_list.html',keyword=keyword,lens=lens,length=length,user_root=user_root,user_ids = user_ids)

# 계정별 키워드 리스트 page show
@app.route('/check/key/<tableName>',methods=['POST','GET'])
def keyword(tableName):
    if not session.get('login'):
        return render_template('/login.html')
    user_root = False
    if session.get('root'):
        user_root = True

    conn = pymysql.connect(host='localhost', user='root', password='1234', db='posco', charset='UTF8MB4')
    curs = conn.cursor(pymysql.cursors.DictCursor)
    sql = "select * from " + tableName
    curs.execute(sql)
    rows = curs.fetchall()
    key_list = []
    idxs = []
    for row in rows:
        key_list.append(row['keyword'])
        idxs.append(row['idx'])
    conn.close()
    length = len(key_list)

    return render_template('/check_keyword.html',key_list=key_list,idxs=idxs,length=length,user_root=user_root)

# 계정별 키워드 추가 rest
@app.route('/check/key/add',methods=['POST','GET'])
def key_add():
    if not session.get('login'):
        return render_template('/login.html')
    user_root = False
    if session.get('root'):
        user_root = True

    conn = pymysql.connect(host='localhost', user='root', password='1234', db='posco', charset='UTF8MB4')
    search = (request.form['search'])
    curs = conn.cursor(pymysql.cursors.DictCursor)
    sql = "insert into keywords_"+session['user_id']+" (keyword) values (%s)"
    curs.execute(sql,(search))
    conn.commit()
    sql = "select * from keywords_" +session['user_id']
    curs.execute(sql)
    rows = curs.fetchall()
    key_list = []
    idxs = []
    for row in rows:
        key_list.append(row['keyword'])
        idxs.append(row['idx'])
    conn.close()
    length = len(key_list)

    return render_template('/check_keyword.html',key_list=key_list,idxs=idxs,length=length,user_root=user_root)

# 계정별 키워드 삭제 rest
@app.route('/check/key/delete/<index>',methods=['GET'])
def key_delete(index):
    if not session.get('login'):
        return render_template('/login.html')
    user_root = False
    if session.get('root'):
        user_root = True
    conn = pymysql.connect(host='localhost', user='root', password='1234', db='posco', charset='UTF8MB4')
    curs = conn.cursor(pymysql.cursors.DictCursor)
    sql = "delete from keywords_"+session['user_id']+" where idx='" +str(index) +"'"
    curs.execute(sql)
    conn.commit()
    curs = conn.cursor(pymysql.cursors.DictCursor)
    sql = "select * from keywords_" + session['user_id']
    curs.execute(sql)
    rows = curs.fetchall()
    key_list = []
    idxs = []
    for row in rows:
        key_list.append(row['keyword'])
        idxs.append(row['idx'])
    conn.close()
    length = len(key_list)

    return render_template('/check_keyword.html',key_list=key_list,idxs=idxs,length=length,user_root=user_root)




if __name__ == '__main__':
    app.run('0.0.0.0', port=4000, threaded=True)



