from django.urls import path
from account.views import (
    SignupView,
    VerifyEmailView
)
urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('verify/email/', SignupView.as_view(), name='verify-email'),
]