import re
import requests
from rest_framework import serializers
from .models import UserInfo, Comment, Attachment
import bleach

# Дозволені HTML теги та атрибути для тексту коментаря
ALLOWED_TAGS = ['a', 'code', 'i', 'strong']
ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title'],
}

# Регулярні вирази для валідації
USERNAME_REGEX = r'^[A-Za-z0-9]+$'
EMAIL_REGEX = r'^[\w\.-]+@[\w\.-]+\.\w+$'
URL_REGEX = r'^(https?://)?([\w\-]+\.)+[\w\-]+(/[\w\-./?%&=]*)?$'

class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = ['file']

    def validate_file(self, file):
        valid_image_types = ['image/jpeg', 'image/png', 'image/gif']
        max_txt_size = 100 * 1024  # 100KB

        content_type = file.content_type
        if content_type in valid_image_types:
            # Тут можна додати додаткову обробку зображень (зменшення розміру)
            return file
        elif content_type == 'text/plain':
            if file.size > max_txt_size:
                raise serializers.ValidationError('Текстовий файл не повинен бути більшим за 100KB.')
            return file
        else:
            raise serializers.ValidationError('Непідтримуваний формат файлу.')

class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserInfo
        fields = ['username', 'email', 'homepage']

    def validate_username(self, value):
        if not re.match(USERNAME_REGEX, value):
            raise serializers.ValidationError('Імʼя користувача має містити лише латинські літери та цифри.')
        return value

    def validate_email(self, value):
        if not re.match(EMAIL_REGEX, value):
            raise serializers.ValidationError('Некоректний формат email.')
        return value

    def validate_homepage(self, value):
        if value and not re.match(URL_REGEX, value):
            raise serializers.ValidationError('Некоректний формат URL.')
        return value

class RecursiveCommentSerializer(serializers.Serializer):
    def to_representation(self, value):
        serializer = CommentSerializer(value, context=self.context)
        return serializer.data

class CommentSerializer(serializers.ModelSerializer):
    user = UserInfoSerializer()
    attachments = AttachmentSerializer(many=True, required=False, read_only=True)
    parent_id = serializers.PrimaryKeyRelatedField(
        queryset=Comment.objects.all(), source='parent', required=False, allow_null=True
    )
    replies = RecursiveCommentSerializer(many=True, read_only=True)
    captcha = serializers.CharField(write_only=True)  # Очікуємо поле captcha

    class Meta:
        model = Comment
        fields = ['id', 'user', 'text', 'created_at', 'parent_id', 'attachments', 'replies', 'captcha']

    def validate_captcha(self, value):
        secret_key = '6LcLxkwrAAAAADIJHHYmzF1DsfN210q6QeQ1F9oP'

        response = requests.post(
            'https://www.google.com/recaptcha/api/siteverify',
            data={
                'secret': secret_key,
                'response': value
            }
        )
        result = response.json()

        if not result.get('success'):
            raise serializers.ValidationError('Невірна CAPTCHA.')
        return value

    def validate_text(self, value):
        # Очищення тексту від небезпечних тегів (XSS)
        cleaned_text = bleach.clean(
            value,
            tags=ALLOWED_TAGS,
            attributes=ALLOWED_ATTRIBUTES,
            strip=True
        )
        return cleaned_text

    def create(self, validated_data):
        validated_data.pop('captcha', None)  # Не зберігаємо капчу

        user_data = validated_data.pop('user')
        user, _ = UserInfo.objects.get_or_create(
            username=user_data['username'],
            email=user_data['email'],
            defaults={'homepage': user_data.get('homepage')}
        )
        comment = Comment.objects.create(user=user, **validated_data)
        return comment
