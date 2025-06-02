from django.urls import path
from .views import CommentListCreateAPIView, CommentDetailAPIView, ReplyCreateAPIView
from .views import RegisterAPIView


urlpatterns = [
    path('comments/', CommentListCreateAPIView.as_view(), name='comment-list-create'),
    path('comments/<int:pk>/', CommentDetailAPIView.as_view(), name='comment-detail'),
    path('comments/reply/', ReplyCreateAPIView.as_view(), name='comment-reply-create'),

    path('register/', RegisterAPIView.as_view(), name='register'),

]
