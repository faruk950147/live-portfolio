from django.urls import path

from account.api_views import (
    RootAPIView
)
urlpatterns = [
    path('', RootAPIView.as_view()),
]