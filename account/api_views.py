from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

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
    def get(self, request):
        return Response({
            "signup": "",
        })