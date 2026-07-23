from django.urls import path
from account.views import (
    SignupView,
    VerifyEmailView,
    LoginView
)
urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('verify-email/', VerifyEmailView.as_view(), name='verify-email'),
    path('login/', LoginView.as_view(), name='login'),
]