from django.urls import path
from . import views


app_name = "chatbot"
urlpatterns = [
    path("save/", views.SaveDBAPIView().as_view()),
]
