
from django.views import generic
from django.shortcuts import render

# Create your views here.
class HomeView(generic.View):
    def get(self, request, *args, **kwargs):
        return render(request, 'home/index.html')
