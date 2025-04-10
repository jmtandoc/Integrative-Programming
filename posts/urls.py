from django.urls import path, include
from .views import PostListCreate, PostDetailView, CommentListCreate, ToggleLikePostView, PostLikesListView
from .views import feed_view
from rest_framework.authtoken.views import obtain_auth_token
from .views import UserRegistrationView

urlpatterns = [
    path('feed/', feed_view, name='feed'),
    path('posts/', PostListCreate.as_view(), name='post-list-create'),
    path('posts/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('comments/', CommentListCreate.as_view(), name='comment-list-create'),
    path('like/<int:post_id>/', ToggleLikePostView.as_view(), name='toggle-like'),
    path('auth/', include('social_django.urls', namespace='social_auth')),
    path('token-auth/', obtain_auth_token, name='api_token_auth'),
    path('users/', UserRegistrationView.as_view(), name='user-registration'),
    path('posts/<int:post_id>/likes/', PostLikesListView.as_view(), name='post-likes-list'), 
]