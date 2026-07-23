from django.views import generic
from django.contrib import messages
from django.shortcuts import render, redirect
from account.forms import (
    SignupForm,
    VerifyEmailForm,
    LoginForm,
)

# ===================== SIGNUP ====================
class SignupView(generic.View):
    def get(self, request):
        return render(request, "account/signup.html", {"form": SignupForm()})

    def post(self, request):
        form = SignupForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("verify-email")

        return render(request, "account/signup.html", {"form": form})
    
# ================= VERIFY EMAIL ======================
class VerifyEmailView(generic.View):
    def get(self, request):
        return render(request, "account/verify_email.html", {"form": VerifyEmailForm()})

    def post(self, request):
        form = VerifyEmailForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "Your email has been verified successfully.")
            return redirect("login")

        return render(request, "account/verify_email.html")
    
























