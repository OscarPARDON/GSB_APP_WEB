from django.contrib import admin # Import Django admin module
from django.urls import path, include # Import URLS Django modules
#################################################################################################################

urlpatterns = [
    path('admin/', admin.site.urls), # URL to the admin access
    path('', include('visitor.urls')), # Default : URL for the visitor part
    path('candidate/', include('candidate.urls')), # URL for the candidate part
]
