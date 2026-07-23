
from django.views import generic
from django.shortcuts import render

from mixins.mixing import LoginRequiredMixin, LogoutRequiredMixin



class HomeView(LoginRequiredMixin, generic.View):
    login_url = 'login'
    def get(self, request):
        return render(request, 'home/index.html')
