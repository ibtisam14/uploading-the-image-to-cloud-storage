from django.urls import path
from .views import register_view, login_view, UploadImageView, UploadImageURLView, my_images

urlpatterns = [
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('upload/', UploadImageView.as_view(), name='upload'),             
    path('upload-url/', UploadImageURLView.as_view(), name='upload-url'),  
    path('my-images/', my_images, name='my-images'),
]
