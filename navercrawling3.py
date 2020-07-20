import ssl                                 #서버 구축에 필요한 모듈
import bs4                                 #BeautifulSoup
import pandas as pd                        #데이터 분석 라이브러리
from datetime import datetime              #현재 시간 구하는 모듈
from datetime import timedelta             #두 날짜와 시간 사이의 차이 계산해줌
import urllib.request as urlopen           #URL 열기위한 라이브러리
import re                                  #(Regular Expressions) 정규표현식 지원
import pymysql                             #Python에서 MySQL 사용할 수 있는 환경 구축
import requests                            #간편한 HTTP 요청처리를 위해 사용하는 모듈





def navercl3(search_pagenumber,search_keyword,search_time):                      #posco.py 에서 navercrawling3.navercl3(양 , 키워드, 기간) 이렇게 불러온다
    title_list = []
    media_list = []
    content_list = []
    addr_list = []
    lists = []
    time = now = datetime.now().strftime("%Y.%m.%d.%H.%M")
    search_pagenumber = int(search_pagenumber)                                                                     #search_pagenumber = 양
    search_endday = time                                                                                           #search_endday = 현재 시간  
    search_startday = (datetime.now() - timedelta(int(search_time))).strftime("%Y.%m.%d.%H.%M")                    #search_startday = 현재시간 - 기간 (startday 부터 endday 까지의 기사 수집)

    conn = pymysql.connect(host='localhost', user='root', password='1234', db='posco', charset='utf8')             #MySQL 연결
    curs = conn.cursor()
    tablename = search_keyword+"_"+str(search_pagenumber)+"_"+datetime.now().strftime("%Y%m%d%H%M")

    #keyword table을 만드는데, 이미 같은 테이블이 있을 경우 삭제하고 새로 만듦
    sql = "show tables like '"+tablename+"'"    #table 조회
    curs.execute(sql)
    if len(curs.fetchall()) == 1:               #table 삭제
        sql = "drop table " + tablename
        curs.execute(sql)

    sql = "create table "+tablename+" ("
    sql += "text_company varchar(20) not null,"
    sql += "text_headline varchar(200) not null,"
    sql += "text_sentence varchar(10000) not null,"
    sql += "addr varchar(1000) not null,"
    sql += "idx integer not null) ENGINE=InnoDB DEFAULT CHARSET=utf8;"
    curs.execute(sql)                                             
    
    #크롤링
    for pagenumber in range(0,search_pagenumber):
        try:
            url = "https://search.naver.com/search.naver?&where=news&query="\
                  +str(search_keyword)+"&ds="\
                  +str(search_startday)+"&de="\
                  +str(search_endday)+"&start="\
                  +str(10*pagenumber+1)+"&refresh_start=0"
            response = requests.get(url)
            html = response.text
            htmlsoup = bs4.BeautifulSoup(html, 'html.parser')

            rawdata = htmlsoup.find("ul", {"class": "type01"})

            # Find title in naver results
            title_data = rawdata.findAll("dt")
            for data in title_data:
                raw = data.find("a")
                title = raw['title']
                title_list.append(title)

            # Find address in naver results
            addr_data = rawdata.findAll("dt")
            for data in addr_data:
                raw = data.find("a")
                addr = raw['href']
                addr_list.append(addr)

            # Find media in naver results
            media_data = rawdata.findAll("dd", {"class": "txt_inline"})
            for data in media_data:
                raw = data.find("span", {"class": "_sp_each_source"})
                media = str(raw.text)
                media = media.replace('언론사 선정', '')
                media_list.append(media)
        except:
            continue

    # Find content in article
    for url in addr_list:
        content_url = url
        content=''
        try:
            context = ssl._create_unverified_context()  # 인증에러를 방지한다
            response = urlopen.urlopen(url, context=context)
            html = response.read().decode("utf-8")
            content_html = bs4.BeautifulSoup(html, "html.parser")

            content_korean = re.compile(r'[^가-힣]+')
            content = content_korean.sub(' ', str(content_html))    #한글(가~힣)을 제외한 모든 문자를 제거
            content_endposition = content.find('기자')
            if content_endposition == -1:
                content_endposition = content.find(r'[가-힣]{2:4}'+'기자')
            content_filtered = content[0:content_endposition]
            if len(content_filtered) < 1000:
                pass
            else:
                content = content_filtered
        except:
            pass
        content_list.append(content)
        print(url)


    # Concentrate lists in list
    size = len(title_list)
    print(size)

    for itemnumber in range(0,size):
        try:
            #articleinfo = []
            #articleinfo.append(title_list[itemnumber])
            #articleinfo.append(media_list[itemnumber])
            #articleinfo.append(addr_list[itemnumber])
            #articleinfo.append(content_list[itemnumber])
            
            #keyword table에 데이터 추가
            sql = "insert into "+tablename+" values (%s, %s, %s, %s, %s)"
            curs.execute(sql, (media_list[itemnumber],title_list[itemnumber],content_list[itemnumber],addr_list[itemnumber],itemnumber+1))

        except:
            continue
    conn.commit()
    conn.close()
    return tablename
