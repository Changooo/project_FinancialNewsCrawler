from selenium import webdriver
import ssl
import bs4
import pandas as pd
from datetime import datetime
from datetime import timedelta
import urllib.request as urlopen
import re
import pymysql




def googlecl2(search_pagenumber,search_keyword,search_time):
    title_list = []
    media_list = []
    content_list = []
    addr_list = []
    lists = []
    #search_pagenumber = int(input("검색할 페이지 수를 입력해주세요.: "))
    #search_keyword = input("검색할 키워드를 입력해주세요.: ")
    #search_startday = input("검색을 시작할 날짜를 형식에 맞춰 입력해주세요.(ex 07/03/2019): ")
    #search_endday = input("검색을 마칠 날짜를 형식에 맞춰 입력해주세요.(ex 07/31/2019): ")
    options = webdriver.ChromeOptions()
    options.add_argument("--headless"); # open Browser in maximized mode
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome('/usr/bin/chromedriver', chrome_options=options)
    driver.implicitly_wait(3)
    time = now = datetime.now().strftime("%Y.%m.%d.%H.%M")
    #yesterday = (datetime.now() - timedelta(1)).strftime("%Y.%m.%d.%H.%M")
    search_pagenumber = int(search_pagenumber)
    search_endday = time
    search_startday = (datetime.now() - timedelta(int(search_time))).strftime("%Y.%m.%d.%H.%M")

    conn = pymysql.connect(host='localhost', user='root', password='1234', db='posco', charset='utf8')
    curs = conn.cursor()
    tablename = search_keyword+"_"+str(search_pagenumber)+"_"+datetime.now().strftime("%Y%m%d%H%M")
    # keyword table을 만드는데, 이미 같은 테이블이 있을 경우 삭제하고 새로 만듦
    sql = "show tables like '"+tablename+"'"        #table 조회
    curs.execute(sql)
    if len(curs.fetchall()) == 1:                   #table 삭제
        sql = "drop table " + tablename
        curs.execute(sql)

    sql = "create table "+tablename+" ("
    sql += "text_company varchar(20) not null,"
    sql += "text_headline varchar(200) not null,"
    sql += "text_sentence varchar(10000) not null,"
    sql += "addr varchar(1000) not null,"
    sql += "idx integer not null)ENGINE=InnoDB DEFAULT CHARSET=utf8;"
    curs.execute(sql)

    for pagenumber in range(0,search_pagenumber):
        try:
            url = "https://www.google.com/search?q="\
                  +str(search_keyword)+"&tbs=cdr:1,cd_min:"\
                  +str(search_startday)+",cd_max:"\
                  +str(search_endday)+"&tbm=nws&start="\
                  +str(10*pagenumber)+"&biw=1536&bih=754&dpr=1.25"

            driver.get(url)
            html = driver.page_source
            htmlsoup = bs4.BeautifulSoup(html, 'html.parser')

            # Find title in google results
            title_data = htmlsoup.findAll("h3")
            for data in title_data:
                title = str(data.text)
                title_list.append(title)

            # Find address in google results
            addr_data = htmlsoup.findAll("div", {"class": "g"})
            for data in addr_data:
                raw = data.find("h3")
                raw_text = str(raw)
                addr_startposition = raw_text.find('href="')
                addr_endposition = raw_text.find('" ping')
                addr = raw_text[addr_startposition + 6:addr_endposition]
                addr_list.append(addr)

            # Find media in google results
            media_data = htmlsoup.findAll("div", {"class": "slp"})
            for data in media_data:
                raw = data.find("span")
                media_endposition = raw.find("(")
                media = raw.text
                media_list.append(media)

        except:
            continue
    driver.quit()


    # Find content in article
    for url in addr_list:
        content_url = url
        #driver.get(content_url)
        #content_html = driver.page_source
        try:
            context = ssl._create_unverified_context()  # 인증에러를 방지한다
            response = urlopen.urlopen(url, context=context)
            html = response.read().decode("utf-8")
            content_html = bs4.BeautifulSoup(html, "html.parser")

            content_korean = re.compile(r'[^가-힣]+')
            content = content_korean.sub(' ', str(content_html))
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
            #lists.append(articleinfo)

            #keyword table에 데이터 추가
            sql = "insert into "+tablename+" values (%s, %s, %s, %s, %s)"
            curs.execute(sql, (media_list[itemnumber],title_list[itemnumber],content_list[itemnumber],addr_list[itemnumber],itemnumber+1))

        except:
            continue
    conn.commit()
    conn.close()
    return tablename
    # Write on CSV
    #data = pd.DataFrame(lists)
    #data.columns = ['기사제목','신문사','기사주소','기사내용']
    #data.to_csv("google_result.csv")
