from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from .models import Post, Comment, Like
from .serializers import PostSerializer, CommentSerializer
from .permissions import IsPostAuthor

CustomUser = get_user_model()


class PostListCreate(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        posts = Post.objects.filter(privacy='public') if request.user.role == 'user' else Post.objects.all()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

    def post(self, request):
        data = request.data.copy()
        data['author'] = request.user.id
        serializer = PostSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostDetailView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsPostAuthor]

    def get(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        if post.privacy == 'private' and post.author != request.user:
            return Response({"detail": "This post is private."}, status=status.HTTP_403_FORBIDDEN)
        self.check_object_permissions(request, post)
        serializer = PostSerializer(post)
        return Response(serializer.data)


class CommentListCreate(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        post_id = request.query_params.get('post')
        comments = Comment.objects.filter(post_id=post_id) if post_id else Comment.objects.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request):
        data = request.data.copy()
        data['author'] = request.user.id
        serializer = CommentSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ToggleLikePostView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        like, created = Like.objects.get_or_create(user=request.user, post=post)
        if not created:
            like.delete()
            return Response({'message': 'Unliked'}, status=200)
        return Response({'message': 'Liked'}, status=201)


# ✅ Optimized Feed View with Pagination + Caching + Query Optimization
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def feed_view(request):
    page = request.GET.get('page', 1)
    cache_key = f"user_{request.user.id}_feed_page_{page}"
    cached_data = cache.get(cache_key)

    if cached_data:
        return Response(cached_data)

    # Query Optimization
    posts = Post.objects.filter(
        author__followers__follower=request.user
    ).select_related('author').prefetch_related('likes', 'comments').order_by('-created_at')

    # Pagination
    paginator = PageNumberPagination()
    paginator.page_size = 10
    result_page = paginator.paginate_queryset(posts, request)
    serialized = PostSerializer(result_page, many=True, context={'request': request})

    # Caching for 5 minutes
    cache.set(cache_key, serialized.data, timeout=300)

    return paginator.get_paginated_response(serialized.data)
