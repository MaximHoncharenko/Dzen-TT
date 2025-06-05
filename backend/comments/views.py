from rest_framework import generics, filters, permissions, serializers
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import PermissionDenied, ValidationError
from .models import Comment
from .serializers import CommentSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
import random
import string
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from django.http import HttpResponse
from django.views.decorators.http import require_GET

class CommentPagination(PageNumberPagination):
    page_size = 25
    page_size_query_param = 'page_size'
    max_page_size = 100


class CommentListCreateAPIView(generics.ListCreateAPIView):
    queryset = Comment.objects.filter(parent=None).order_by('-created_at')
    serializer_class = CommentSerializer
    pagination_class = CommentPagination
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['user__username', 'created_at']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CommentDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_update(self, serializer):
        if serializer.instance.user != self.request.user:
            raise PermissionDenied('Ви не маєте права редагувати цей коментар.')
        serializer.save()

    def perform_destroy(self, instance):
        if instance.user != self.request.user:
            raise PermissionDenied('Ви не маєте права видаляти цей коментар.')
        instance.delete()


class ReplyCreateAPIView(generics.CreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        parent_id = self.request.data.get('parent_id')
        if not parent_id:
            raise ValidationError({'parent_id': 'Обовʼязково вказати parent_id для відповіді.'})
        try:
            parent = Comment.objects.get(pk=parent_id)
        except Comment.DoesNotExist:
            raise ValidationError({'parent_id': 'Коментар з таким ID не знайдено.'})
        serializer.save(user=self.request.user, parent=parent)


class RegisterAPIView(APIView):
    def post(self, request):
        username = request.data.get('username')
        email = request.data.get('email', '')
        password = request.data.get('password')

        if not username or not password:
            return Response({'error': 'Потрібні username та password'}, status=400)

        if User.objects.filter(username=username).exists():
            return Response({'error': 'Користувач з таким імʼям вже існує'}, status=400)

        try:
            validate_password(password)
        except ValidationError as e:
            return Response({'error': e.messages}, status=400)

        user = User.objects.create_user(username=username, email=email, password=password)
        return Response({'message': 'Користувач створений'}, status=201)

# -------------------------------
# HTML-сторінка з вбудованим JS
# -------------------------------

def index(request):
    html = """
    <!DOCTYPE html>
    <html lang="uk">
    <head>
        <meta charset="UTF-8" />
        <title>API документація</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .btn {
                display: inline-block;
                padding: 16px 32px;
                margin: 20px;
                font-size: 18px;
                background: #1b563f;
                color: #fff;
                border: none;
                border-radius: 8px;
                text-decoration: none;
                transition: background 0.2s;
            }
            .btn:hover { background: #14512d; }
        </style>
    </head>
    <body>
        <h1>API документація</h1>
        <a href="/swagger/" class="btn">Swagger UI</a>
        <a href="/redoc/" class="btn">Redoc</a>
    </body>
    </html>
    """
    return HttpResponse(html)

@require_GET
def captcha_image(request):
    # Генерируем случайную строку
    code = ''.join(random.choices(string.ascii_letters + string.digits, k=5))
    request.session['captcha_code'] = code

    # Создаём изображение
    img = Image.new('RGB', (120, 40), color=(255, 255, 255))
    d = ImageDraw.Draw(img)
    # Можно указать свой путь к TTF-файлу шрифта
    try:
        font = ImageFont.truetype("arial.ttf", 28)
    except:
        font = ImageFont.load_default()
    d.text((10, 5), code, font=font, fill=(0, 0, 0))

    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    return HttpResponse(buffer, content_type='image/png')
