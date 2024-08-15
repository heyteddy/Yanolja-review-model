# 야놀자 n개월 200(20*10)개 데이터 크롤링
import json
import sys
import time
from bs4 import BeautifulSoup
from selenium import webdriver


# 크롤링 함수
# 필요한 것 : 날짜, 평점, 리뷰텍스트
def crawl_yanolja_reviews(name, url):
    review_list = []
    driver = webdriver.Chrome()
    driver.get(url)
    
    time.sleep(3)

    # scroll
    scroll_count=20
    for i in range(scroll_count):
        driver.execute_script('window.scrollTo(0, document.body.scrollHeight)')
        time.sleep(2)

    # html 소스 가져오기 & parsing
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    # 리뷰컨테이너 정보, 중요
    review_containers = soup.select('#__next > section > div > div.css-1js0bc8 > div > div > div')
    review_date = soup.select('#__next > section > div > div.css-1js0bc8 > div > div > div > div.css-1ivchjf > div > p')

    # 리뷰 컨테이너에서 리뷰 텍스트, 별점 추출
    for i in range(len(review_containers)):
        review_text = review_containers[i].find('p', class_='content-text').text
        review_stars = review_containers[i].find_all('path', {'fill':'#FDBD00'})
        star_cnt = len(review_stars)
        if review_date:
            date = review_date[i].get_text(strip=True)

        review_dict={
            'review': review_text,
            'stars': star_cnt,
            'date': date
        }

        review_list.append(review_dict)

    # 가져온 정보를 파일에 저장
    with open(f'./res/{name}.json', 'w', encoding='utf-8') as f:
        json.dump(review_list, f, indent=4, ensure_ascii=False)

# 파일 실행
if __name__ == '__main__':
    name, url = sys.argv[1], sys.argv[2]
    crawl_yanolja_reviews(name=name, url=url)

#__next > section > div > div.css-1js0bc8 > div:nth-child(1) > div:nth-child(2) > div > div.css-8ehu1o > div:nth-child(1) > div.css-1ivchjf > p