from django.urls import path
from . import views

urlpatterns = [
    # signup
    path('users/signup', views.UserSignUpView.as_view(), name='user-signup'),
    path('admin/signup', views.AdminSignUpView.as_view(), name='admin-signup'),

    # login
    path('login', views.LoginView.as_view(), name='login'),

    # schduled-tasks
    path('scheduled-tasks', views.ScheduledTaskView.as_view(), name='task'),

    # google login
    path('login/google', views.GoogleOAuthLogin.as_view(), name='login'),
    path('google/callback', views.GoogleOAuthCallback.as_view(), name='callback'),

    # otp login
    path('login/otp', views.OTPLoginView.as_view(), name='otp-login'),
    path('login/otp/verify', views.OTPVerifyView.as_view(), name='otp-verify'),

    # logout
    path('logout', views.LogoutView.as_view(), name='logout')
]