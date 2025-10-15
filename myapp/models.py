# models.py
from django.db import models

class UploadedImage(models.Model):
    name = models.CharField(max_length=255)
    image_url = models.URLField()
    file_id = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name