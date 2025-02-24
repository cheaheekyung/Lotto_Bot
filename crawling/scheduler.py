from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from .crawling import crawl_website   # 크롤링함수 임포트


def start_scheduler():
    """
    Description : 크롤링 자동화를 위한 함수
    
    - apscheduler 라이브러리를 사용해 정해진 시간에 크롤링 작업을 수행하게하는 함수
    - 이때 시간 기준은 settings.py 에서 설정한 TimeZone 기준
    - chatbot/apps.py 에서 ready()함수를 만들어 앱이 실행되면 저절로 스케줄러가 시작되게 설정 -> runserver를 하면 앱이 실행되고 스케줄러도
    """
    
    scheduler = BackgroundScheduler()
    
    # 매주 토요일 22:00에 크롤링 작업 실행 -> 크롤링 작업: crawling.py 에 있는 crawl_website함수 호출
    scheduler.add_job(crawl_website, CronTrigger(hour=22, minute=3, day_of_week='6'))
    #테스트용
    # scheduler.add_job(crawl_website, CronTrigger(hour=18, minute=17))
    
    # 스케줄러 시작
    scheduler.start()