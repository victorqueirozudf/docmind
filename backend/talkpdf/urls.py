from django.urls import path
from . import views
from .views import PDFChatView, PDFChatDetailView

app_name = 'talkpdf'

urlpatterns = [
    path('chats/', PDFChatView.as_view()),
    path('chats/delete/<slug:thread_id>/', PDFChatView.as_view()),
    path('chats/<slug:thread_id>/', PDFChatDetailView.as_view()),
]
