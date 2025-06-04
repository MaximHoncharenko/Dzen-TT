from django.urls import path
from .views import CommentListCreateAPIView, CommentDetailAPIView, ReplyCreateAPIView
<<<<<<< HEAD
from .views import RegisterAPIView, captcha_image
from django.conf import settings
from django.conf.urls.static import static
=======
from .views import RegisterAPIView
>>>>>>> 87de69ce221dc6cf0d22ed8ea060621e465c5864


urlpatterns = [
    path('comments/', CommentListCreateAPIView.as_view(), name='comment-list-create'),
    path('comments/<int:pk>/', CommentDetailAPIView.as_view(), name='comment-detail'),
    path('comments/reply/', ReplyCreateAPIView.as_view(), name='comment-reply-create'),

    path('register/', RegisterAPIView.as_view(), name='register'),

<<<<<<< HEAD
    path('captcha/', captcha_image, name='captcha_image'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

=======
]
>>>>>>> 87de69ce221dc6cf0d22ed8ea060621e465c5864
