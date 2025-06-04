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
        <title>Коментарі</title>
        <style>
            body {{{{ font-family: Arial, sans-serif; margin: 20px; }}}}
            .comment {{{{ border: 1px solid #ccc; padding: 10px; margin-bottom: 10px; }}}}
            .reply {{{{ margin-left: 30px; }}}}
            .author {{{{ font-weight: bold; }}}}
            textarea {{{{ width: 100%; height: 60px; }}}}
            button {{{{ margin-top: 5px; }}}}
        </style>
    </head>
    <body>

    <h1>Коментарі</h1>

    <div id="comments-container"></div>

    <h2>Додати новий коментар</h2>
    <textarea id="new-comment-text" placeholder="Ваш коментар..."></textarea><br/>
    <input type="text" id="captcha" placeholder="Введіть CAPTCHA: abcd" /><br/>
    <button onclick="addComment()">Відправити</button>

    <script>
        async function fetchComments() {{{{
            const res = await fetch('/api/comments/');
            const data = await res.json();
            const container = document.getElementById('comments-container');
            container.innerHTML = '';
            data.results.forEach comment => {{{{
                container.appendChild(renderComment(comment));
            }}}});
        }}}}

        function renderComment(comment, isReply = false) {{{{
            const div = document.createElement('div');
            div.className = 'comment' + (isReply ? ' reply' : '');
            div.dataset.id = comment.id;

            const author = document.createElement('div');
            author.className = 'author';
            author.textContent = comment.user.username || 'Анонім';
            div.appendChild(author);

            const text = document.createElement('div');
            text.textContent = comment.text;
            div.appendChild(text);

            const replyBtn = document.createElement('button');
            replyBtn.textContent = 'Відповісти';
            replyBtn.onclick = () => {{{{
                if (div.querySelector('textarea')) return;
                const textarea = document.createElement('textarea');
                textarea.placeholder = 'Ваша відповідь...';
                const captcha = document.createElement('input');
                captcha.placeholder = 'CAPTCHA: abcd';
                const sendBtn = document.createElement('button');
                sendBtn.textContent = 'Відправити відповідь';
                sendBtn.onclick = () => addReply(comment.id, textarea.value, captcha.value);
                div.appendChild(textarea);
                div.appendChild(captcha);
                div.appendChild(sendBtn);
            }}}};
            div.appendChild(replyBtn);

            if (comment.replies && comment.replies.length > 0) {{{{
                comment.replies.forEach(reply => {{{{
                    div.appendChild(renderComment(reply, true));
                }}}});
            }}}}

            return div;
        }}}}

        async function addComment() {{{{
            const text = document.getElementById('new-comment-text').value.trim();
            const captcha = document.getElementById('captcha').value.trim();
            if (!text || !captcha) {{{{
                alert('Заповніть усі поля');
                return;
            }}}}
            await sendComment(text, null, captcha);
            document.getElementById('new-comment-text').value = '';
            document.getElementById('captcha').value = '';
            fetchComments();
        }}}}

        async function addReply(parentId, text, captcha) {{{{
            if (!text.trim() || !captcha.trim()) {{{{
                alert('Заповніть всі поля');
                return;
            }}}}
            await sendComment(text, parentId, captcha);
            fetchComments();
        }}}}

        async function sendComment(text, parentId, captcha) {{{{
            const res = await fetch('/api/comments/', {{{{
                method: 'POST',
                headers: {{{{
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer ' + localStorage.getItem('access')
                }}}},
                body: JSON.stringify({{{{text, parent_id: parentId, captcha}}}})
            }}}});
            if (!res.ok) {{{{
                const err = await res.json();
                alert('Помилка: ' + JSON.stringify(err));
            }}}}
        }}}}

        fetchComments();
    </script>

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
