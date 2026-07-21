from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from account.serializers import (
    SignupSerializer,
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
        })

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


        
