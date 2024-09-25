from django.urls import path

from . import views
from .views import MessageTalkPdfView

urlpatterns = [
    path('', views.index, name='index'),
    path('message/', MessageTalkPdfView.as_view()),
]
