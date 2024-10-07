from django.urls import path

from . import views
from .views import PDFProcessView

urlpatterns = [
    path('message/', PDFProcessView.as_view()),
]
