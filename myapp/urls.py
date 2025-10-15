from django.urls import path
from .views import register_view, login_view, UploadImageView

urlpatterns = [
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('upload/', UploadImageView.as_view(), name='upload'),
]
