from django.urls import path

from . import views
from .views import PDFChatView, PDFChatDetailView

urlpatterns = [
    path('chats/', PDFChatView.as_view()),
    path('chats/<slug:thread_id>/', PDFChatDetailView.as_view()),
]
