from django.urls import path

from . import views
from .models import MessageTalkPdf
from .views import UserPdfView, MessageTalkPdfView

urlpatterns = [
    path('', views.index, name='index'),
    path('basic/', UserPdfView.as_view()),
    path('message/', MessageTalkPdfView.as_view()),
]
