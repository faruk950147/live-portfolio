from django.urls import path

from account.api_views import (
    RootAPIView,
    SignupViewAPI
)
urlpatterns = [
    path('', RootAPIView.as_view()),
    path('signup/', SignupViewAPI.as_view()),
]