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
