from django.views import generic
from django.shortcuts import render

# Create your views here.
class SignupView(generic.View):
    def get(self, request, *args, **kwargs):
        return render(request, 'account/signup.html')