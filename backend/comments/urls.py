from django.urls import path
from .views import CommentListCreateAPIView, CommentDetailAPIView, ReplyCreateAPIView
from . import views

urlpatterns = [
    path('comments/', CommentListCreateAPIView.as_view(), name='comment-list-create'),
    path('comments/<int:pk>/', CommentDetailAPIView.as_view(), name='comment-detail'),
    path('comments/reply/', ReplyCreateAPIView.as_view(), name='comment-reply-create'),
    path('list/', views.get_comments, name='comments-list'),
    path('add/', views.add_comment, name='comments-add'),
    path('page/', views.comments_page, name='comments-page'),
]
