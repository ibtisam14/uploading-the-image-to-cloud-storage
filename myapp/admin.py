from django.contrib import admin
from .models import UploadedImage

@admin.register(UploadedImage)
class UploadedImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'user_id_display', 'name', 'image_url', 'file_id', 'uploaded_at')
    search_fields = ('name', 'file_id', 'user__username', 'user__id')
    list_filter = ('uploaded_at', 'user')
    ordering = ('-uploaded_at',)

    def user_id_display(self, obj):
        return obj.user.id

    user_id_display.short_description = 'User ID'
