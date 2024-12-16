from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('dj_rest_auth.urls')),  # Login, Logout, Password Reset, etc.
    # path('api/auth/registration/', include('dj_rest_auth.registration.urls')),  # Registration
    path('api/', include('api.urls')),
    path('api/', include('user.urls')), 
] + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
