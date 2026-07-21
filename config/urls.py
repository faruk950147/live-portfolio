from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    # Website URLs
    path('', include('home.urls')),
    path('account/', include('account.urls')),
    
    # API endpoints    
    path('api/home', include('home.api_urls')),
    path('api/account/', include('account.api_urls')),

    # Admin site
    path('admin/', admin.site.urls),
]
