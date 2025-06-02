from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from PIL import Image
import os
import bleach

ALLOWED_TAGS = ['a', 'code', 'i', 'strong']
ALLOWED_ATTRIBUTES = {'a': ['href', 'title']}


def validate_file_extension(value):
    ext = os.path.splitext(value.name)[1].lower()
    valid_image_extensions = ['.jpg', '.jpeg', '.gif', '.png']
    valid_text_extensions = ['.txt']
    if ext not in valid_image_extensions + valid_text_extensions:
        raise ValidationError('Unsupported file extension.')


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    username = models.CharField(max_length=32, blank=True)
    email = models.EmailField(blank=True)
    homepage = models.URLField(blank=True)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')

    def clean_text(self):
        return bleach.clean(self.text, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES, strip=True)

    def save(self, *args, **kwargs):
        self.text = self.clean_text()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Comment by {self.user.username} on {self.created_at.strftime("%Y-%m-%d %H:%M:%S")}'


class Attachment(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='attachments/', validators=[validate_file_extension])
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        ext = os.path.splitext(self.file.name)[1].lower()
        if ext == '.txt' and self.file.size > 100 * 1024:
            raise ValidationError("Text files must be less than 100 KB.")

        if ext in ['.jpg', '.jpeg', '.gif', '.png']:
            try:
                img = Image.open(self.file)
                if img.width > 320 or img.height > 240:
                    img.thumbnail((320, 240), Image.Resampling.LANCZOS)
                    from io import BytesIO
                    from django.core.files.base import ContentFile
                    buffer = BytesIO()
                    img_format = img.format or 'JPEG'
                    img.save(buffer, format=img_format)
                    buffer.seek(0)
                    new_file = ContentFile(buffer.read())
                    new_name = os.path.splitext(self.file.name)[0] + '.' + img_format.lower()
                    self.file.save(new_name, new_file, save=False)
            except Exception:
                raise ValidationError("Invalid image file.")
        super().save(*args, **kwargs)

    def __str__(self):
        return f'File for Comment {self.comment.id}'
