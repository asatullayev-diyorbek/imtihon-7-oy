from django.urls import path

from . import views

app_name = 'user'
urlpatterns = [
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/update/photo/', views.UpdateProfileImageView.as_view(), name='update_photo'),
    path('profile/update/password/', views.PasswordChangeView.as_view(), name='password_change'),
    path('profile/update/info/', views.UpdateProfileView.as_view(), name='update_info'),
    path('register/', views.Register.as_view(), name='register'),
    path('login/', views.Login.as_view(), name='login'),
    path('logout/', views.logout_user, name='logout'),

    path('reset/', views.ResetPasswordView.as_view(), name='password_reset'),
    path('reset/confirm/<uidb64>/<token>/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
]

