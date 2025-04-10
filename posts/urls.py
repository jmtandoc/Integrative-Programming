from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from .views import PostListCreate, PostDetailView, CommentListCreate, ToggleLikePostView, feed_view

urlpatterns = [
    path('posts/', PostListCreate.as_view(), name='post-list-create'),
    path('posts/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('comments/', CommentListCreate.as_view(), name='comment-list-create'),
    path('posts/<int:post_id>/like/', ToggleLikePostView.as_view(), name='toggle-like'),
    path('feed/', feed_view, name='feed'),
    path('api-token-auth/', obtain_auth_token, name='api-token-auth'),  # Token authentication
]