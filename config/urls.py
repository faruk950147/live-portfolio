from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    # Website URLs
    path('account/', include('account.urls')),
    
    # API endpoints    
    path('api/account/', include('account.api_urls')),

    
    # Admin site
    path('admin/', admin.site.urls),
]
