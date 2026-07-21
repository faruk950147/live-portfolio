from django.urls import path
from account.views import (
    SignupView,
)
urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
]