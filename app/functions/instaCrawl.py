import os
from selenium import webdriver
import time
import pandas as pd
import numpy as np
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import re
import datetime
from tqdm import tqdm
from .db_models import CORPUS
from . import database
#### config를 아예 다른 폴더로 빼놓고 독립적으로 관리하는 방식
# import sys
# sys.path.append('opt/settings')
# import config 

#### config를 내부에 넣고, 환경변수로 관리하는 방식
insta_email = os.getenv('INSTA_EMAIL')
insta_password = os.getenv('INSTA_PASSWORD')

INSTA_CONFIG = {
    'email':insta_email,
    'password':insta_password
}

# corpus 폴더 내 파일 존재여부 확인
def check_txt(category, dt_now):
    data = database.get_by_category_time(CORPUS, category, dt_now)
    if data.count() == 0:
        return False
    
    


# 검색어 조건에 따라 url 생성
def insta_seraching(word):
    url = "https://www.instagram.com/explore/tags/" + str(word)
    return url

# 열린 페이지에서 첫번째 게시물 클릭 + 3초 슬립
def select_first(driver):
    first = driver.find_elements(By.CSS_SELECTOR,"div._aagw")[0]
    first.click()
    time.sleep(3)

# 본문 내용만 리스트로 corpus형태 가져오기
def get_content(driver):
    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')
    #본문 내용
    try:
        content = soup.select('div._a9zs')[0].text
    except:
        content = ''
    
    return content

# 본문 내용, 작성일자, 좋아요 수, 위치 정보, 해시태그 가져오기
def get_All_content(driver):
    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')
    #본문 내용
    try:
        content = soup.select('div._a9zs')[0].text
    except:
        content = ''
    
    #해시태그
    tags = re.findall(r'#[^\s#,\\]+', content)

    #작성 일자
    date = soup.select('time._aaqe')[0]['datetime'][:10]

    #좋아요
    try:
        like = soup.select('div._aacl._aaco._aacw._aacx._aada._aade')[0].findAll('span')[-1].text
    except:
        like = 0

    #위치
    try:
        place = soup.select('div._aaqm')[0].text
    except:
        place = ''
    
    data = {'content':content, 'date':date, 'like':like, 'place':place, 'tags':tags}
    return data

# 첫번째 게시물 클릭 후 다음 게시물 클릭
def move_next(driver):
    try:
        right = driver.find_element(By.CSS_SELECTOR,'div._aaqg._aaqh')
        right.click()
        time.sleep(3)
    except:
        print("move_next error")
        time.sleep(1)
    



# step4.인스타그램 로그인 함수 정의
def login(id, pw, driver):
    # 로그인 페이지로 이동
    driver.get("https://www.instagram.com/accounts/login/")
    time.sleep(5)
    
    # id와 pw를 입력하는 창의 요소 정보 획득
    input = driver.find_elements(By.TAG_NAME,"input")

    # 아이디를 입력
    input[0].send_keys(id)

    # 비밀번호 입력
    input[1].send_keys(pw)

    # 엔터
    input[1].send_keys(Keys.RETURN)
    time.sleep(8)

    # 로그인 정보 저장 여부 팝업창 제거 ("나중에 하기 버튼 클릭")
    try:
        btn_later1 = driver.find_element(By.CLASS_NAME,'_acan._acao._acas')
        btn_later1.click()
        time.sleep(5)
    except:
        btn_later1 = ''

    # 알림 설정 팝업창 제거 ("나중에 하기 버튼 클릭")
    try:
        btn_later2 = driver.find_element(By.CLASS_NAME,'_a9--._a9_1')
        btn_later2.click()
    except:
        pass


# 요청시 word에 해당하는 태그로 인스타검색 후 결과반환
def get_results(word, num=10):
    # 크롤링 시작
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('window-size=1920x1080')
    options.add_argument("disable-gpu")
    options.add_argument(f'user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.87 Safari/537.36')
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    # 크롬 브라우저 열기
    driver = webdriver.Chrome('chrome/chromedriver.exe', chrome_options=options)

    driver.get('https://www.instagram.com/accounts/login/')
    time.sleep(3)

    login(INSTA_CONFIG['email'],INSTA_CONFIG['password'], driver)
    url = insta_seraching(word)

    driver.get(url)
    time.sleep(10)

    select_first(driver)

    results = []

    target = num - 1
    for i in tqdm(range(target)):
        try:
            dict_data = get_All_content(driver)
            results.append(dict_data)
            move_next(driver)
        except:
            time.sleep(2)
            move_next(driver)
        time.sleep(3)

    return results

def get_corpus(word_list, num=10):
    # 크롤링 시작
    expected_time = 13 + (num * 3) * len(word_list)
    dt_now = datetime.datetime.now().date()
    print(f"예상소요시간 : {expected_time}초")
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('window-size=1920x1080')
    options.add_argument("disable-gpu")
    options.add_argument(f'user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.87 Safari/537.36')
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    # 크롬 브라우저 열기
    driver = webdriver.Chrome('chromedriver.exe', chrome_options=options)
    driver.get('https://www.instagram.com/accounts/login/')
    time.sleep(3)

    login(INSTA_CONFIG['email'], INSTA_CONFIG['password'], driver)
    target = num - 1

    for word in tqdm(word_list):
        if check_txt(word, dt_now):
            continue
        url = insta_seraching(word)

        driver.get(url)
        time.sleep(10)
        
        try:
            select_first(driver)
        except:
            continue

        
        for i in range(target):
            try:
                content_data = get_content(driver)
                database.add_instance(CORPUS,\
                          text=content_data,\
                          category=word,\
                          g_time=dt_now)
                move_next(driver)
            except:
                time.sleep(2)
                move_next(driver)
            time.sleep(3)
        print(f"{word} 완료!")
        
        


    return

# 하루에 한번, 모든 insta_corpus를 저장합니다.
def Setting_all_corpus():
    categorys = ['포기김치', '반찬세트', '장아찌', '절임류', '기타반찬류', '단무지', '조림류', '장조림', '볶음류',
       '젓갈장류', '된장', '김해초', '과일', '견과류', '채소', '쌀', '잡곡혼합곡', '건과류', '쇠고기',
       '닭고기', '돼지고기', '알류', '축산가공식품', '기타육류', '양고기', '오리고기', '한방재료',
       '건강분말', '건강즙과일즙', '꿀', '인삼', '홍삼', '건강환정', '영양제', '비타민제',
       '환자식영양보충식', '꽁치고등어', '골뱅이번데기', '햄', '참치연어', '기타통조림캔', '황도과일', '생선',
       '해산물어패류', '피클올리브', '건어물', '차류', '주스과즙음료', '전통차음료', '건강기능성음료',
       '우유요구르트', '커피', '청량탄산음료', '코코아', '두유', '탄산수', '어묵', '기타조미료', '고추장',
       '별미김치', '백김치', '파김치', '갓김치', '열무김치', '깍두기', '절임배추', '액젓', '옥수수콩',
       '면류', '총각김치', '세트', '겉절이', '물엿올리고당', '즉석국즉석탕', '기타소스드레싱',
       '기타냉동간편조리식품', '카레짜장', '스낵', '가루분말류', '오이소박이', '튀김류', '수산가공식품',
       '채식푸드', '양념장', '곤약', '간장', '가공안주류', '초콜릿', '떡', '한과', '쿠키',
       '아이스크림빙수', '빵', '강정', '팝콘강냉이류', '시리얼', '젤리', '전병', '엿', '푸딩', '사탕',
       '화과자', '껌', '만두', '기타장류', '식초', '라면', '단백질보충제', '기타다이어트식품', '굴소스',
       '청국장', '쌈장', '메주', '누룽지', '즉석밥', '샐러드', '스프', '죽', '간식디저트', '떡볶이',
       '피자', '핫도그', '딤섬', '도시락', '햄버거', '고춧가루', '소금', '고추냉이', '겨자', '설탕',
       '후추', '천연감미료', '마요네즈', '오리엔탈드레싱', '스파게티파스타소스', '머스타드소스', '칠리핫소스',
       '케첩', '돈가스소스', '스테이크바베큐소스', '발사믹드레싱', '딸기잼', '기타잼시럽', '치즈', '마가린',
       '버터', '생크림', '휘핑크림', '연유', '콜라겐', '가르시니아', '히알루론산', '식이섬유',
       '다이어트차', '구이', '찌개국', '맛살게살', '함박미트볼', '식용유오일', '제과제빵재료', '막걸리탁주',
       '약주', '소주', '일반증류주', '리큐르주', '기타주류', '전통주선물세트', '과실주', '생수', '케이크',
       '기타과자', '대상별', '기능별', '비타민', '유산균', '도시락밥류', '샐러드닭가슴살', '죽스프',
       '만두딤섬', '떡볶이튀김어묵', '피자핫도그햄버거', '기타간편조리식품', '베이커리', '젤리캐러멜푸딩',
       '사탕껌엿', '과자쿠키', '팝콘강냉이', '전통과자', '제로음료', '우유요거트', '파우더스무디', '면파스타',
       '밥죽', '볶음튀김', '조림찜']
    get_corpus(categorys)