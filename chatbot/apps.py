from django.apps import AppConfig


class ChatbotConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'chatbot'
    
    
    def ready(self):
        """
        Description : 앱이 시작될때마다 스케줄러가 실행되도록 하는 함수
        
        - manage.py runserver 로 서버를 실행하면 앱이 로드되고 그 앱의 apps.py 에있는 ready()함수도 실행
        - 서버가 시작되면 자동으로 apscheduler 스케줄러가 시작되고 정해진시간에 크롤링작업을 수행하도록 하기 위함
        """
        from crawling.scheduler import start_scheduler
        start_scheduler()
