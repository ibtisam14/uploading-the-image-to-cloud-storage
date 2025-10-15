from django.contrib import admin
from .models import UploadedImage

@admin.register(UploadedImage)
class UploadedImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'image_url', 'file_id', 'uploaded_at')
    search_fields = ('name', 'file_id')
    list_filter = ('uploaded_at',)
    ordering = ('-uploaded_at',)
