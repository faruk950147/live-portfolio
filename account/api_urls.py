from django.urls import path

from account.api_views import (
    RootAPIView,
    SignupViewAPI,
    VerifyEmailViewAPI,
    LoginViewAPI,
)
urlpatterns = [
    path('', RootAPIView.as_view()),
    path('signup/', SignupViewAPI.as_view()),
    path('verify/email/', VerifyEmailViewAPI.as_view()),
    path('login/', LoginViewAPI.as_view())
]