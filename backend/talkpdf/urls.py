from django.urls import path

from . import views
from .views import PDFChatView, PDFChatDetailView, HomeView#, register_user

urlpatterns = [
    # teste autenticação
    path('home/', HomeView.as_view(), name='home'),
    path('logout/', views.LogoutView.as_view(), name ='logout'),

    path('chats/', PDFChatView.as_view()),
    path('chats/<slug:thread_id>/', PDFChatDetailView.as_view()),
]
