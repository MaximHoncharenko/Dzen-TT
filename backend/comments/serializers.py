import requests
import bleach
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Comment, Attachment

ALLOWED_TAGS = ['a', 'code', 'i', 'strong']
ALLOWED_ATTRIBUTES = {'a': ['href', 'title']}


class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = ['file']


class RecursiveCommentSerializer(serializers.Serializer):
    def to_representation(self, value):
        serializer = CommentSerializer(value, context=self.context)
        return serializer.data


class CommentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    attachments = AttachmentSerializer(many=True, read_only=True)
    parent_id = serializers.PrimaryKeyRelatedField(queryset=Comment.objects.all(), source='parent', required=False)
    replies = RecursiveCommentSerializer(many=True, read_only=True)
    captcha = serializers.CharField(write_only=True)
    username = serializers.CharField(required=False, allow_blank=True, max_length=32)
    email = serializers.EmailField(required=False, allow_blank=True)
    homepage = serializers.URLField(required=False, allow_blank=True)

    class Meta:
        model = Comment
        fields = [
            'id', 'user', 'username', 'email', 'homepage', 'text', 'created_at',
            'parent_id', 'attachments', 'replies', 'captcha'
        ]

    def validate_captcha(self, value):
        request = self.context.get('request')
        if not request:
            raise serializers.ValidationError('Не вдалося перевірити CAPTCHA.')
        code = request.session.get('captcha_code')
        if not code or value.strip().lower() != code.lower():
            raise serializers.ValidationError('Невірна CAPTCHA.')
        return value

    def validate_text(self, value):
        return bleach.clean(value, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES, strip=True)

    def validate(self, data):
        user = self.context['request'].user
        if not user.is_authenticated:
            # Аноним: username и email обязательны
            if not data.get('username') or not data.get('email'):
                raise serializers.ValidationError("User Name и Email обовʼязкові для анонімних коментарів.")
            import re
            if not re.match(r'^[A-Za-z0-9]+$', data['username']):
                raise serializers.ValidationError("User Name: тільки латиниця і цифри.")
        return data

    def create(self, validated_data):
        request = self.context.get('request')
        file = request.FILES.get('file')
        validated_data.pop('captcha', None)
        comment = Comment.objects.create(**validated_data)
        if file:
            Attachment.objects.create(comment=comment, file=file)
        return comment
