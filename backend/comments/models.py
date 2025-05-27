from django.db import models
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from PIL import Image
import bleach
import os

ALLOWED_TAGS = ['a', 'code', 'i', 'strong']
ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title'],
}

def validate_file_extension(value):
    ext = os.path.splitext(value.name)[1].lower()
    valid_image_extensions = ['.jpg', '.jpeg', '.gif', '.png']
    valid_text_extensions = ['.txt']

    if ext not in valid_image_extensions + valid_text_extensions:
        raise ValidationError('Unsupported file extension.')

class UserInfo(models.Model):
    username = models.CharField(
        max_length=50,
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z0-9]+$',
                message='Username must contain only Latin letters and digits.'
            )
        ]
    )
    email = models.EmailField()
    homepage = models.URLField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.username


class Comment(models.Model):
    user = models.ForeignKey(UserInfo, on_delete=models.CASCADE)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def clean_text(self):
        cleaned = bleach.clean(self.text, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES, strip=True)
        return cleaned

    def save(self, *args, **kwargs):
        self.text = self.clean_text()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Comment by {self.user.username} on {self.created_at.strftime("%Y-%m-%d %H:%M:%S")}'


class Attachment(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='attachments/', validators=[validate_file_extension])
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        super().clean()
        if self.file.size > 100 * 1024:  # 100 KB
            ext = os.path.splitext(self.file.name)[1].lower()
            if ext == '.txt':
                raise ValidationError("Text files must be less than 100 KB.")
        
        ext = os.path.splitext(self.file.name)[1].lower()
        if ext in ['.jpg', '.jpeg', '.gif', '.png']:
            try:
                img = Image.open(self.file)
                max_width, max_height = 320, 240
                if img.width > max_width or img.height > max_height:
                    img.thumbnail((max_width, max_height), Image.ANTIALIAS)
                    from io import BytesIO
                    from django.core.files.base import ContentFile
                    
                    buffer = BytesIO()
                    img.save(buffer, format=img.format)
                    self.file.save(self.file.name, ContentFile(buffer.getvalue()), save=False)
            except Exception as e:
                raise ValidationError("Invalid image file.")

    def __str__(self):
        return f'File for Comment {self.comment.id}'
