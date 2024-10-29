from .views import UserView, VerifyTokenView, RegisterUserView, LogoutView
from django.urls import path

app_name = 'authentication'

urlpatterns = [
    path('login/', UserView.as_view(), name='login'),
    path('signup/', RegisterUserView.as_view(), name='signup'),
    path('logout/', LogoutView.as_view(), name ='logout'),
    path('verify_token', VerifyTokenView.as_view(), name='verify-token')
]