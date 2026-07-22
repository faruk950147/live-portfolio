from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from account.serializers import (
    SignupSerializer,
    VerifyEmailSerializer,
    LoginSerializer,
    LogoutSerializer,
    
)

def success(message, data=None, code=200):
    return Response({
        "success": True,
        "message": message,
        "data": data
    }, status=code)


def error(message, code=400):
    return Response({
        "success": False,
        "message": message
    }, status=code)
    
    
class RootAPIView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        return Response({
            "signup": "http://127.0.0.1:8000/api/account/signup/",
            "verify_email": "http://127.0.0.1:8000/api/account/verify/email/",
            "login": "http://127.0.0.1:8000/api/account/login/",
        })

# ============================ SIGNUP ============================
class SignupViewAPI(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return success(
            "Signup successful. Verify your email.",
            {"user_id": user.id},
            status.HTTP_201_CREATED
        )

# ============================ VERIFY EMAIL ============================
class VerifyEmailViewAPI(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = VerifyEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return success("Email verified successfully")

# =========================== LOGIN ============================
class LoginViewAPI(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response(
            serializer.validated_data,
            status=status.HTTP_200_OK,
        )
        
# ========================= LOGOUT =============================
class LogoutView(APIView):
    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"message": "Logout successful."},
            status=status.HTTP_200_OK
        )

        
        
        
        
