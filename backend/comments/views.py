from rest_framework import generics, filters, permissions, serializers, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, ValidationError
from .models import Comment
from .serializers import CommentSerializer

class CommentPagination(PageNumberPagination):
    page_size = 25
    page_size_query_param = 'page_size'
    max_page_size = 100

class CommentListCreateAPIView(generics.ListCreateAPIView):
    """
    Список кореневих коментарів (без батька) та створення нового коментаря.
    """
    queryset = Comment.objects.filter(parent=None).order_by('-created_at')
    serializer_class = CommentSerializer
    pagination_class = CommentPagination
    permission_classes = [permissions.AllowAny]  # Можна змінити на IsAuthenticated

    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['user__username', 'user__email', 'created_at']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        captcha = self.request.data.get('captcha', '')
        if captcha.lower() != 'abcd':
            raise serializers.ValidationError({'captcha': 'Невірна CAPTCHA.'})

        if self.request.user.is_authenticated:
            # Якщо користувач авторизований - прив’язуємо його як user
            serializer.save(user=self.request.user)
        else:
            # Інакше використовуємо дані з серіалізатора
            serializer.save()

class ReplyCreateAPIView(generics.CreateAPIView):
    """
    Створення відповіді (вкладеного коментаря) до існуючого коментаря.
    """
    serializer_class = CommentSerializer
    permission_classes = [permissions.AllowAny]  # Змінити при необхідності

    def perform_create(self, serializer):
        captcha = self.request.data.get('captcha', '')
        if captcha.lower() != 'abcd':
            raise serializers.ValidationError({'captcha': 'Невірна CAPTCHA.'})

        parent_id = self.request.data.get('parent_id')
        if not parent_id:
            raise ValidationError({'parent_id': 'Обовʼязково вказати parent_id для відповіді.'})

        try:
            parent_comment = Comment.objects.get(pk=parent_id)
        except Comment.DoesNotExist:
            raise ValidationError({'parent_id': 'Коментар з таким ID не знайдено.'})

        if self.request.user.is_authenticated:
            serializer.save(user=self.request.user, parent=parent_comment)
        else:
            serializer.save(parent=parent_comment)

class CommentDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    Отримання, редагування і видалення конкретного коментаря.
    Редагувати і видаляти може лише автор коментаря.
    """
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.AllowAny]  # Поставити IsAuthenticated, якщо треба

    def perform_update(self, serializer):
        if self.request.user.is_authenticated:
            if serializer.instance.user != self.request.user:
                raise PermissionDenied('Ви не маєте права редагувати цей коментар.')
        else:
            raise PermissionDenied('Тільки авторизовані користувачі можуть редагувати коментарі.')
        serializer.save()

    def perform_destroy(self, instance):
        if self.request.user.is_authenticated:
            if instance.user != self.request.user:
                raise PermissionDenied('Ви не маєте права видаляти цей коментар.')
        else:
            raise PermissionDenied('Тільки авторизовані користувачі можуть видаляти коментарі.')
        instance.delete()

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse
from django.shortcuts import render
import json
from comments.models import Comment  # замініть на ваші моделі

def comments_page(request):
    # просто рендеримо HTML сторінку
    return render(request, 'comments_page.html')


def serialize_comment(comment):
    # серіалізуємо коментар в словник для JSON
    return {
        'id': comment.id,
        'text': comment.text,
        'author': comment.author.username if comment.author else "Anonymous",
        'parent_id': comment.parent.id if comment.parent else None,
        'replies': [serialize_comment(reply) for reply in comment.replies.all()]
    }


def get_comments(request):
    # отримуємо тільки батьківські коментарі, з відповідями
    comments = Comment.objects.filter(parent__isnull=True).prefetch_related('replies')
    data = [serialize_comment(c) for c in comments]
    return JsonResponse(data, safe=False)


@csrf_exempt  # для спрощення (у продакшені треба CSRF захист)
def add_comment(request):
    if request.method != 'POST':
        return HttpResponseBadRequest("Invalid method")
    try:
        data = json.loads(request.body)
        text = data.get('text')
        parent_id = data.get('parent_id')
        if not text:
            return HttpResponseBadRequest("Text is required")

        parent = None
        if parent_id:
            parent = Comment.objects.filter(id=parent_id).first()

        comment = Comment.objects.create(text=text, parent=parent, author=request.user if request.user.is_authenticated else None)
        return JsonResponse(serialize_comment(comment))
    except Exception as e:
        return HttpResponseBadRequest(str(e))
    
    from django.http import HttpResponse
from django.utils.html import format_html

def comments_page(request):
    html = format_html("""
    <!DOCTYPE html>
    <html lang="uk">
    <head>
        <meta charset="UTF-8" />
        <title>Коментарі</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .comment {{ border: 1px solid #ccc; padding: 10px; margin-bottom: 10px; }}
            .reply {{ margin-left: 30px; }}
            .author {{ font-weight: bold; }}
            textarea {{ width: 100%; height: 60px; }}
            button {{ margin-top: 5px; }}
        </style>
    </head>
    <body>

    <h1>Коментарі</h1>

    <div id="comments-container"></div>

    <h2>Додати новий коментар</h2>
    <textarea id="new-comment-text" placeholder="Ваш коментар..."></textarea><br/>
    <button onclick="addComment()">Відправити</button>

    <script>
        async function fetchComments() {{
            const res = await fetch('/api/comments/list/');
            const comments = await res.json();
            const container = document.getElementById('comments-container');
            container.innerHTML = '';
            comments.forEach(comment => {{
                container.appendChild(renderComment(comment));
            }});
        }}

        function renderComment(comment, isReply = false) {{
            const div = document.createElement('div');
            div.className = 'comment' + (isReply ? ' reply' : '');
            div.dataset.id = comment.id;

            const author = document.createElement('div');
            author.className = 'author';
            author.textContent = comment.author;
            div.appendChild(author);

            const text = document.createElement('div');
            text.textContent = comment.text;
            div.appendChild(text);

            const replyBtn = document.createElement('button');
            replyBtn.textContent = 'Відповісти';
            replyBtn.onclick = () => {{
                if (div.querySelector('textarea')) return;
                const textarea = document.createElement('textarea');
                textarea.placeholder = 'Ваша відповідь...';
                const sendBtn = document.createElement('button');
                sendBtn.textContent = 'Відправити відповідь';
                sendBtn.onclick = () => addReply(comment.id, textarea.value);
                div.appendChild(textarea);
                div.appendChild(sendBtn);
            }}
            div.appendChild(replyBtn);

            if (comment.replies && comment.replies.length > 0) {{
                comment.replies.forEach(reply => {{
                    div.appendChild(renderComment(reply, true));
                }});
            }}

            return div;
        }}

        async function addComment() {{
            const text = document.getElementById('new-comment-text').value.trim();
            if (!text) {{
                alert('Напишіть коментар!');
                return;
            }}
            await sendComment(text, null);
            document.getElementById('new-comment-text').value = '';
            fetchComments();
        }}

        async function addReply(parentId, text) {{
            if (!text.trim()) {{
                alert('Напишіть відповідь!');
                return;
            }}
            await sendComment(text, parentId);
            fetchComments();
        }}

        async function sendComment(text, parentId) {{
            const res = await fetch('/api/comments/add/', {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}},
                body: JSON.stringify({{text: text, parent_id: parentId}})
            }});
            if (!res.ok) {{
                alert('Помилка при відправці коментаря');
            }}
        }}

        fetchComments();
    </script>

    </body>
    </html>
    """)
    return HttpResponse(html)
