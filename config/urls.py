from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
    # Website URLs
    path('', include('home.urls')),
    path('account/', include('account.urls')),
    
    # API endpoints    
    path('api/home', include('home.api_urls')),
    path('api/account/', include('account.api_urls')),

    # JWT Auth
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # Admin site
    path('admin/', admin.site.urls),
]
