from django.urls import path
from .views import UserDetailView, UserUpdateView

urlpatterns = [
    path('user/details/', UserDetailView.as_view(), name='user-details'),
    path('user/update/', UserUpdateView.as_view(), name='user-update'),
]
