from django.urls import path, include
from .views import PostListCreate, PostDetailView, CommentListCreate, ToggleLikePostView
from .views import feed_view

urlpatterns = [
    path('feed/', feed_view, name='feed'),
    path('posts/', PostListCreate.as_view(), name='post-list-create'),
    path('posts/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('comments/', CommentListCreate.as_view(), name='comment-list-create'),
    path('like/<int:post_id>/', ToggleLikePostView.as_view(), name='toggle-like'),
    path('auth/', include('social_django.urls', namespace='social_auth')),
]
