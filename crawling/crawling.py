import requests
from bs4 import BeautifulSoup
from datetime import datetime
from chatbot.models import LottoDraw

def crawl_website():
    """
    Description : 크롤링을 진행하는 함수

    - requests, BeautifulSoup4 라이브러리를 사용해 크롤링 진행
    - 크롤링 후 데이터 파싱 + 작성한 ERD 기반으로 저장가능하게 데이터 타입 변환
    - DB에 저장 -> 중복 방지를 위해 저장할회차가 DB 에 없는 경우만 진행
    - 자동화를 위해 apscheduler 라이브러리를 사용 -> scheduler.py 에서 특정시간에 이 함수를 호출함
    """
    
    url = "https://www.dhlottery.co.kr/gameResult.do?method=byWin"   # 크롤링할 url 주소
    response = requests.get(url)                                     # requests 를 사용해 HTML 가져오기
    soup = BeautifulSoup(response.text, 'html.parser')               # requests 로 가져온 HTML소스를 파싱,조작 등을 할수있는 뷰티풀숲 객체 생성
    
    # 데이터 추출
    draw_result = soup.select('div.win_result h4')                   # 회차 정보
    draw_date = soup.select('p.desc')                                # 추첨일
    win_numbers = soup.select('div.num.win span.ball_645')           # 당첨번호
    bonus_ball = soup.select('div.num.bonus span.ball_645')          # 보너스 번호
    
    # 데이터 파싱 + 설계한 ERD 기반으로 데이터타입 변환
    draw_result = int(''.join(filter(str.isdigit, draw_result[0].text)))
    draw_date = draw_date[0].text.strip()
    draw_date = draw_date.strip("()").replace("년 ", ".").replace("월 ", ".").replace("일 추첨", "").strip()
    draw_date = datetime.strptime(draw_date, "%Y.%m.%d").date()
    win_numbers = ",".join([str(n.text.strip()) for n in win_numbers])
    bonus_ball = int(bonus_ball[0].text.strip())
    
    # DB 저장 -> 중복 방지 : 저장할 회차가 DB에 없는 경우만
    if not LottoDraw.objects.filter(round_no=draw_result).exists():
        LottoDraw.objects.create(
            round_no=draw_result,
            draw_date=draw_date,
            winning_numbers=win_numbers,
            bonus_number=bonus_ball
        )
        print("크롤링후 DB저장 완료!")
    else:
        print("크롤링완료!, DB에 동일한 회차 정보가 이미있어서 추가저장은 안함!")
    
    # 결과 정리
    result = {
        "회차": draw_result,
        "추첨일": draw_date,
        "당첨번호": win_numbers,
        "보너스번호": bonus_ball
    }
    
    return print("크롤링 완료!\n" + f"{result}")   # {'회차': 1159, '추첨일': datetime.date(2025, 2, 15), '당첨번호': '3,9,27,28,38,39', '보너스번호': 7}