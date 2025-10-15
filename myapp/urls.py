# urls.py (in your app or project)
from django.urls import path
from . import views

urlpatterns = [
    path('', views.upload_page, name='upload_page'),
    path('upload/', views.upload_image, name='upload_image'),
]