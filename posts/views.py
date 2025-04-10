from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.core.cache import cache
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.authtoken.models import Token
from .models import Post, Comment, Like
from .serializers import PostSerializer, CommentSerializer
from .permissions import IsPostAuthor

CustomUser = get_user_model()


class PostListCreate(generics.ListCreateAPIView):
    """Optimized Post List & Create View using DRF Generics"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = PostSerializer

    def get_queryset(self):
        """Optimized query filtering based on user role"""
        user = self.request.user
        return Post.objects.filter(privacy='public') if user.role == 'user' else Post.objects.all()

    def perform_create(self, serializer):
        """Set author field automatically"""
        serializer.save(author=self.request.user)


class PostDetailView(generics.RetrieveDestroyAPIView):
    """Improved Post Detail View with permissions"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsPostAuthor]
    serializer_class = PostSerializer
    queryset = Post.objects.all()

    def get(self, request, *args, **kwargs):
        """Ensure private posts remain private"""
        post = self.get_object()
        if post.privacy == 'private' and post.author != request.user:
            return Response({"detail": "This post is private."}, status=status.HTTP_403_FORBIDDEN)
        return super().get(request, *args, **kwargs)


class CommentListCreate(generics.ListCreateAPIView):
    """Optimized Comment List & Create View"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = CommentSerializer

    def get_queryset(self):
        """Filter comments based on post ID if provided"""
        post_id = self.request.query_params.get('post')
        return Comment.objects.filter(post_id=post_id) if post_id else Comment.objects.all()

    def perform_create(self, serializer):
        """Set author field automatically"""
        serializer.save(author=self.request.user)


class ToggleLikePostView(APIView):
    """Like & Unlike Post View"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        like, created = Like.objects.get_or_create(user=request.user, post=post)

        if not created:
            like.delete()
            return Response({'message': 'Unliked'}, status=status.HTTP_200_OK)
        return Response({'message': 'Liked'}, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def feed_view(request):
    """Optimized feed with caching and pagination"""
    page = request.GET.get('page', 1)
    cache_key = f"user_{request.user.id}_feed_page_{page}"
    cached_data = cache.get(cache_key)

    if cached_data:
        return Response(cached_data)

    posts = Post.objects.filter(
        author__followers__follower=request.user
    ).select_related('author').prefetch_related('likes', 'comments').order_by('-created_at')

    paginator = PageNumberPagination()
    paginator.page_size = 10
    result_page = paginator.paginate_queryset(posts, request)
    serialized = PostSerializer(result_page, many=True, context={'request': request})

    cache.set(cache_key, serialized.data, timeout=300)

    return paginator.get_paginated_response(serialized.data)