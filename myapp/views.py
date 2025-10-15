from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from imagekitio import ImageKit
from imagekitio.models.UploadFileRequestOptions import UploadFileRequestOptions
from .models import UploadedImage
from .serializers import RegisterSerializer
import traceback
import requests  

User = get_user_model()

imagekit = ImageKit(
    public_key=settings.IMAGEKIT["public_key"],
    private_key=settings.IMAGEKIT["private_key"],
    url_endpoint=settings.IMAGEKIT["url_endpoint"]
)


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        tokens = get_tokens_for_user(user)
        return Response({
            'user': {
                'id': user.id,
                'email': user.email,
                'username': user.username
            },
            'tokens': tokens
        })
    return Response(serializer.errors, status=400)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    email = request.data.get('email')
    password = request.data.get('password')

    try:
        user = User.objects.get(email=email)
        user = authenticate(username=user.username, password=password)
    except User.DoesNotExist:
        user = None

    if user:
        tokens = get_tokens_for_user(user)
        return Response({
            'user': {
                'id': user.id,
                'email': user.email
            },
            'tokens': tokens
        })
    return Response({'error': 'Invalid credentials'}, status=401)


class UploadImageView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not request.FILES.get("image"):
            return Response({"error": "No image provided"}, status=400)

        uploaded_file = request.FILES["image"]

        try:
            file_bytes = uploaded_file.read()
            upload_options = UploadFileRequestOptions(
                folder="/django_uploads/",
                use_unique_file_name=True,
                is_private_file=False
            )

            result = imagekit.upload_file(
                file=file_bytes,
                file_name=uploaded_file.name,
                options=upload_options
            )

            if result and hasattr(result, 'file_id'):
                uploaded_img = UploadedImage.objects.create(
                    user=request.user,
                    name=result.name,
                    image_url=result.url,
                    file_id=result.file_id
                )
                return Response({
                    "success": True,
                    "url": uploaded_img.image_url,
                    "id": uploaded_img.id
                })

            return Response({"error": "Upload failed"}, status=500)

        except Exception as e:
            print("Upload error:", traceback.format_exc())
            return Response({"error": str(e)}, status=500)

class UploadImageURLView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not request.FILES.get("image"):
            return Response({"error": "No image provided"}, status=400)

        uploaded_file = request.FILES["image"]
        upload_url = "https://upload.imagekit.io/api/v1/files/upload"

        try:
            private_key = settings.IMAGEKIT["private_key"]
            auth = (private_key, "")

            payload = {
                "fileName": uploaded_file.name,
                "folder": "/django_uploads/",
                "useUniqueFileName": "true",
                "isPrivateFile": "false",
            }

            files = {
                "file": uploaded_file.read(),
            }

            response = requests.post(upload_url, files=files, data=payload, auth=auth)
            result = response.json()

            if response.status_code == 200:
                uploaded_img = UploadedImage.objects.create(
                    user=request.user,
                    name=result.get("name"),
                    image_url=result.get("url"),
                    file_id=result.get("fileId")
                )
                return Response({
                    "success": True,
                    "url": uploaded_img.image_url,
                    "id": uploaded_img.id
                })
            else:
                return Response({
                    "error": result.get("message", "Upload failed"),
                    "details": result
                }, status=response.status_code)

        except Exception as e:
            print("Upload error:", traceback.format_exc())
            return Response({"error": str(e)}, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def my_images(request):
    user = request.user
    images = UploadedImage.objects.filter(user=user).values('id', 'name', 'image_url', 'uploaded_at')
    return Response({
        "user": user.username,
        "total_images": images.count(),
        "images": list(images)
    })
