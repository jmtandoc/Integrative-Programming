from django.contrib.auth.models import User, Group
from django.contrib.auth.hashers import make_password
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import api_view
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Post, Comment
from .serializers import UserSerializer, PostSerializer, CommentSerializer
from .permissions import IsPostAuthor
from factories.post_factory import PostFactory
from singletons.config_manager import ConfigManager
from singletons.logger_singleton import LoggerSingleton
from django.views import View
from django.http import JsonResponse

logger = LoggerSingleton().get_logger()
config = ConfigManager()

# Register endpoint
@api_view(['POST'])
def register(request):
    logger.info("Registration attempt")
    serializer = UserSerializer(data=request.data)

    if serializer.is_valid():
        user = serializer.save()
        try:
            user_group = Group.objects.get(name='User')
            user.groups.add(user_group)
        except Group.DoesNotExist:
            logger.error("Group 'User' does not exist.")
            return Response({"detail": "Group 'User' does not exist."}, status=status.HTTP_400_BAD_REQUEST)

        logger.info(f"User '{user.username}' registered successfully.")
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    logger.warning("Invalid registration data.")
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Token retrieval endpoint
@api_view(['POST'])
def obtain_token(request):
    logger.info("Token request initiated")
    username = request.data.get("username")
    password = request.data.get("password")

    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        logger.warning("Invalid username during token request")
        return Response({"detail": "Invalid username or password."}, status=status.HTTP_400_BAD_REQUEST)

    if user.check_password(password):
        refresh = RefreshToken.for_user(user)
        logger.info(f"Token issued for user '{username}'")
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })
    
    logger.warning("Invalid password during token request")
    return Response({"detail": "Invalid username or password."}, status=status.HTTP_400_BAD_REQUEST)


# Register view using class-based API view
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        logger.info("User registration via RegisterView")
        data = request.data
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')

        if not username or not password or not email:
            logger.error("Missing registration fields")
            return Response({"error": "Username, password, and email are required."}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            logger.warning(f"Username '{username}' already exists")
            return Response({"error": "Username already taken."}, status=status.HTTP_400_BAD_REQUEST)

        hashed_password = make_password(password)
        user = User.objects.create(username=username, password=hashed_password, email=email)
        user_group = Group.objects.get(name='User')
        user.groups.add(user_group)
        logger.info(f"User '{username}' registered via RegisterView")

        return Response({"message": "User registered successfully!"}, status=status.HTTP_201_CREATED)


# View for list and creation of users (admin only)
class UserListCreate(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        logger.info("User list requested")
        if not request.user.is_staff:
            logger.warning("Unauthorized user list access attempt")
            return Response({"detail": "Not authorized."}, status=status.HTTP_403_FORBIDDEN)

        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request):
        if not request.user.is_staff:
            logger.warning("Unauthorized user creation attempt")
            return Response({"detail": "Not authorized."}, status=status.HTTP_403_FORBIDDEN)

        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user_group = Group.objects.get(name='User')
            user.groups.add(user_group)
            logger.info(f"User '{user.username}' created by admin")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        logger.error("User creation failed: invalid data")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# View for creating posts
class PostListCreate(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        logger.info("Post list requested")
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

    def post(self, request):
        logger.info("Post creation attempt")
        data = request.data.copy()
        data['author'] = request.user.id
        serializer = PostSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            logger.info("Post created successfully")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        logger.error("Post creation failed")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# View for post details (only author can access)
class PostDetailView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsPostAuthor]

    def get(self, request, pk):
        logger.info(f"Post detail requested for post id {pk}")
        post = get_object_or_404(Post, pk=pk)
        self.check_object_permissions(request, post)
        serializer = PostSerializer(post)
        return Response(serializer.data)


# Factory-based post creation view
class CreatePostFactoryView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logger.info("Post creation using PostFactory")
        data = request.data
        try:
            post = PostFactory.create_post(
                post_type=data['post_type'],
                title=data['title'],
                content=data.get('content', ''),
                metadata=data.get('metadata', {})
            )
            logger.info(f"Factory post created with ID {post.id}")
            return Response({'message': 'Post created successfully!', 'post_id': post.id}, status=status.HTTP_201_CREATED)
        except ValueError as e:
            logger.error(f"Post creation error: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# Class-based view for Comment List and Create
class CommentListCreate(APIView):
    def get(self, request):
        comments = Comment.objects.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Protected view example
class ProtectedView(View):
    def get(self, request):
        return JsonResponse({"message": "This is a protected view"})

