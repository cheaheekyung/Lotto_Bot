from django.urls import path
from . import views


app_name = "chatbot2"
urlpatterns = [
    path('chat/', views.ChatAPIView.as_view(), name='chat'),
]
