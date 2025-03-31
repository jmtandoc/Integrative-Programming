from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import User, Post
from .serializers import UserSerializer, PostSerializer


# View for creating and retrieving users
class UserListCreate(APIView):
    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)  # Return list of all users

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)  # Successfully created
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # Validation errors

# View for creating and retrieving posts
class PostListCreate(APIView):
    def get(self, request):
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)  # Return list of all posts

    def post(self, request):
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)  # Successfully created
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # Validation errors
