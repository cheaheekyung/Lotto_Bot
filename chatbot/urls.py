# chatbot/urls.py

from django.urls import path
from .views import (
    ChatbotHomeView, 
    CSRFTokenView, 
    ChatAPIView, 
    DataStatusView,     # views.py에 있는 이름과 일치하게 수정
    SaveDBAPIView,
    HistoryAPIView
)

app_name = 'chatbot'

urlpatterns = [
    path('', ChatbotHomeView.as_view(), name='chat'),
    path('csrf/', CSRFTokenView.as_view(), name='csrf-token'),
    path('chat/', ChatAPIView.as_view(), name='chat'),
    path('status/', DataStatusView.as_view(), name='status'),
    path('history/', HistoryAPIView.as_view(), name='history'),
    path("save/db/", SaveDBAPIView().as_view()),
]