from rest_framework import serializers
from .models import Post, Comment

class PostSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')  # Prevent manual author assignment

    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'privacy', 'author', 'created_at']

class CommentSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')

    class Meta:
        model = Comment
        fields = ['id', 'post', 'text', 'author', 'created_at']