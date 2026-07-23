from django.views import generic
from django.shortcuts import render
from account.forms import (
    SignupForm
)

# Create your views here.
class SignupView(generic.View):
    def get(self, request):
        return render(request, 'account/signup.html')