from rest_framework import serializers
from .models import Post, Comment, CustomUser
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'role']  # Add any new fields, like 'role'
class PostSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField()
    likes_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    class Meta:
        model = Post
        fields = ['id', 'content', 'created_at', 'author', 'likes_count', 'comments_count']
    def get_likes_count(self, obj):
        return obj.likes.count()
    def get_comments_count(self, obj):
        return obj.comments.count()
class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'content', 'author', 'post', 'created_at']