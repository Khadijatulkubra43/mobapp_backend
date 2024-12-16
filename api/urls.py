from django.urls import path
from .views import GetUserName, IsLoggedin, ImageUploadView, CustomRegisterView

urlpatterns = [
    path('username/', GetUserName.as_view(), name="get-username"),
    path('checkLogin/', IsLoggedin.as_view(), name="get-loginStatus"),
    path('upload/', ImageUploadView.as_view(), name='image-upload'),
     path('auth/registration/', CustomRegisterView.as_view(), name='custom_register'),
]
