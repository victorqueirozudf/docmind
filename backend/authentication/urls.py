from .views import UserView, VerifyTokenView, RegisterUserView, LogoutView, UserDetailView, ListUsersView, DeleteUserView, ResetPasswordView, CreateUserView, ChangePasswordView
from django.urls import path

app_name = 'authentication'

urlpatterns = [
    path('login/', UserView.as_view(), name='login'),
    path('user/', UserDetailView.as_view(), name='user-detail'),
    path('list-users/', ListUsersView.as_view(), name='list-users'),
    path('signup/', RegisterUserView.as_view(), name='signup'),
    path('logout/', LogoutView.as_view(), name ='logout'),
    path('delete/<int:user_id>', DeleteUserView.as_view(), name='delete-user'),
    path('reset-password/<int:user_id>', ResetPasswordView.as_view(), name='reset-password'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('create-user/', CreateUserView.as_view(), name='create-user'),
    path('verify-token', VerifyTokenView.as_view(), name='verify-token')
]