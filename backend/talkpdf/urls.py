from django.urls import path

from . import views
from .views import MessageTalkPdfView, ask_question

urlpatterns = [
    path('', views.index, name='index'),
    path('message/', MessageTalkPdfView.as_view()),
    path('ask/', ask_question, name='ask_question'),
]
