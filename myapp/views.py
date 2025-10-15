from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from imagekitio.models.UploadFileRequestOptions import UploadFileRequestOptions
from imagekitio import ImageKit
import json
from .models import UploadedImage  

# Initialize ImageKit client
imagekit = ImageKit(
    public_key=settings.IMAGEKIT["public_key"],
    private_key=settings.IMAGEKIT.get("private_key"),
    url_endpoint=settings.IMAGEKIT["url_endpoint"]
)

def upload_page(request):
    """Render upload form"""
    return render(request, "upload.html")

@csrf_exempt
def upload_image(request):
    if request.method == "POST" and request.FILES.get("image"):
        uploaded_file = request.FILES["image"]
        try:
            # Read file bytes
            file_bytes = uploaded_file.read()

            # Create upload options OBJECT
            upload_options = UploadFileRequestOptions(
                folder="/django_uploads/",
                use_unique_file_name=True,
                is_private_file=False
            )

            # Upload to ImageKit
            result = imagekit.upload_file(
                file=file_bytes,
                file_name=uploaded_file.name,
                options=upload_options
            )

            # ✅ FIXED: Access result attributes directly
            if result and hasattr(result, 'file_id'):
                # Save to Django model using direct attribute access
                uploaded_img = UploadedImage.objects.create(
                    name=result.name,
                    image_url=result.url,
                    file_id=result.file_id
                )

                return JsonResponse({
                    "success": True,
                    "url": uploaded_img.image_url,
                    "id": uploaded_img.id
                })
            else:
                return JsonResponse({
                    "success": False,
                    "error": "Upload failed: No valid response from ImageKit"
                }, status=500)

        except Exception as e:
            import traceback
            print("Upload error:", traceback.format_exc())
            return JsonResponse({
                "success": False,
                "error": f"Upload failed: {str(e)}"
            }, status=500)

    return JsonResponse({"success": False, "error": "No image provided"}, status=400)