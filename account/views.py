from django.views import generic
from django.contrib import messages
from django.contrib.auth import login, logout
from django.shortcuts import render, redirect
from account.forms import (
    SignupForm,
    VerifyEmailForm,
    LoginForm,
    ChangePasswordForm,
    PasswordResetForm,
    PasswordResetConfirmForm,
    ResendVerifyEmailForm,
)
from mixins.mixing import LoginRequiredMixin, LogoutRequiredMixin

# ===================== SIGNUP ====================
class SignupView(LogoutRequiredMixin, generic.View):
    logout_url = 'logout'
    def get(self, request):
        return render(request, "account/signup.html", {"form": SignupForm()})

    def post(self, request):
        form = SignupForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("verify-email")

        return render(request, "account/signup.html", {"form": form})
    
# ================= VERIFY EMAIL ======================
class VerifyEmailView(LogoutRequiredMixin, generic.View):
    logout_url = 'logout'
    def get(self, request):
        return render(request, "account/verify_email.html", {"form": VerifyEmailForm()})

    def post(self, request):
        form = VerifyEmailForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "Your email has been verified successfully.")
            return redirect("login")

        return render(request, "account/verify_email.html")
    

# =================== LOGIN =========================
# =================== LOGIN =========================
class LoginView(LogoutRequiredMixin, generic.View):
    logout_url = "logout"

    def get(self, request):
        form = LoginForm(request=request)
        return render(request, "account/login.html", {"form": form})

    def post(self, request):
        form = LoginForm(request.POST, request=request)

        if form.is_valid():
            user = form.cleaned_data["user"]

            login(request, user)

            # Remember me
            if not form.cleaned_data.get("keep_logged_in"):
                request.session.set_expiry(0)

            messages.success(request, "You are logged in.")
            return redirect("home")

        return render(request, "account/login.html", {"form": form})

# =================== LOGOUT =========================
class LogoutView(LoginRequiredMixin, generic.View):
    login_url = 'login'
    def get(self, request):
        logout(request)
        messages.success(request, "You are logged out.")
        return redirect('login') 


# =================== CHANGE PASSWORD ==================
class ChangePasswordView(LoginRequiredMixin, generic.View):
    login_url = 'login'
    template_name = "account/change_password.html"

    def get(self, request, *args, **kwargs):
        form = ChangePasswordForm(request=request)
        return render(request, self.template_name, {"form": form})

    def post(self, request, *args, **kwargs):
        form = ChangePasswordForm(request.POST, request=request)

        if form.is_valid():
            form.save()
            messages.success(request, "Password changed successfully.")
            return redirect("change_password")  
        return render(request, self.template_name, {"form": form})


# ========================= PASSWORD RESET REQUEST =========================
class PasswordResetView(generic.View):
    logout_url = 'logout'
    template_name = "account/password_reset.html"

    def get(self, request, *args, **kwargs):
        form = PasswordResetForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request, *args, **kwargs):
        form = PasswordResetForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "If an account with that email exists, an OTP has been sent.")
            return redirect("password_reset_verify")

        return render(request, self.template_name, {"form": form})


# ========================= PASSWORD RESET CONFIRM =========================
class PasswordResetConfirmView(generic.View):
    logout_url = 'logout'
    template_name = "account/password_reset_confirm.html"

    def get(self, request, *args, **kwargs):
        form = PasswordResetConfirmForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request, *args, **kwargs):
        form = PasswordResetConfirmForm(request.POST)

        if form.is_valid():
            form.save()

            messages.success(request, "Your password has been reset successfully. Please log in.")

            return redirect("login") 

        return render(request, self.template_name, {"form": form})


# ===================== RESEND EMAIL ================================
class ResendVerifyEmailView(generic.View):
    logout_url = 'logout'
    template_name = "account/resend_verify_email.html"

    def get(self, request, *args, **kwargs):
        form = ResendVerifyEmailForm()
        return render(request, self.template_name, { "form": form})

    def post(self, request, *args, **kwargs):
        form = ResendVerifyEmailForm(request.POST)

        if form.is_valid():
            form.save()

            messages.success(request, "A new verification code has been sent to your email.")

            return redirect("verify_email") 

        return render(request, self.template_name, {"form": form})











