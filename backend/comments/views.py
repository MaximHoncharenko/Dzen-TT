from rest_framework import generics, filters, permissions, serializers, status
from rest_framework.pagination import PageNumberPagination
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
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['user__username', 'user__email', 'created_at']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        captcha = self.request.data.get('captcha', '')
        if captcha.lower() != 'abcd':
            raise serializers.ValidationError({'captcha': 'Невірна CAPTCHA.'})

        if self.request.user.is_authenticated:
            serializer.save(user=self.request.user)
        else:
            serializer.save()


class CommentDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    Перегляд, оновлення та видалення одного коментаря.
    """
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.AllowAny]

    def perform_update(self, serializer):
        if self.request.user.is_authenticated:
            if serializer.instance.user != self.request.user:
                raise PermissionDenied('Ви не маєте права редагувати цей коментар.')
            serializer.save()
        else:
            raise PermissionDenied('Тільки авторизовані користувачі можуть редагувати.')

    def perform_destroy(self, instance):
        if self.request.user.is_authenticated:
            if instance.user != self.request.user:
                raise PermissionDenied('Ви не маєте права видаляти цей коментар.')
            instance.delete()
        else:
            raise PermissionDenied('Тільки авторизовані користувачі можуть видаляти.')

class ReplyCreateAPIView(generics.CreateAPIView):
    """
    Створення відповіді (вкладеного коментаря) до існуючого коментаря.
    """
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]


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


# -------------------------------
# HTML-сторінка з вбудованим JS
# -------------------------------

from django.http import HttpResponse
from django.utils.html import format_html

def index(request):
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
    <input type="text" id="captcha" placeholder="Введіть CAPTCHA: abcd" /><br/>
    <button onclick="addComment()">Відправити</button>

    <script>
        async function fetchComments() {{
            const res = await fetch('/api/comments/');
            const data = await res.json();
            const container = document.getElementById('comments-container');
            container.innerHTML = '';
            data.results.forEach(comment => {{
                container.appendChild(renderComment(comment));
            }});
        }}

        function renderComment(comment, isReply = false) {{
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
            replyBtn.onclick = () => {{
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
            }};
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
            const captcha = document.getElementById('captcha').value.trim();
            if (!text || !captcha) {{
                alert('Заповніть усі поля');
                return;
            }}
            await sendComment(text, null, captcha);
            document.getElementById('new-comment-text').value = '';
            document.getElementById('captcha').value = '';
            fetchComments();
        }}

        async function addReply(parentId, text, captcha) {{
            if (!text.trim() || !captcha.trim()) {{
                alert('Заповніть всі поля');
                return;
            }}
            await sendComment(text, parentId, captcha);
            fetchComments();
        }}

        async function sendComment(text, parentId, captcha) {{
            const res = await fetch('/api/comments/', {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}},
                body: JSON.stringify({{text, parent_id: parentId, captcha}})
            }});
            if (!res.ok) {{
                const err = await res.json();
                alert('Помилка: ' + JSON.stringify(err));
            }}
        }}

        fetchComments();
    </script>

    </body>
    </html>
    """)
    return HttpResponse(html)
