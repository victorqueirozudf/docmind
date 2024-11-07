from .views import UserView, VerifyTokenView, RegisterUserView, LogoutView, UserDetailView
from django.urls import path

app_name = 'authentication'

urlpatterns = [
    path('login/', UserView.as_view(), name='login'),
    path('user/', UserDetailView.as_view(), name='user-detail'),
    path('signup/', RegisterUserView.as_view(), name='signup'),
    path('logout/', LogoutView.as_view(), name ='logout'),
    path('verify-token', VerifyTokenView.as_view(), name='verify-token')
]