from rest_framework import serializers
from .models import User, Post

# Serializer for User model
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'created_at']

# Serializer for Post model with validation for assigned_to
class PostSerializer(serializers.ModelSerializer):
    # String representation of the assigned user for readability
    assigned_to = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'content', 'author', 'assigned_to', 'created_at']

    # Custom validation to ensure the assigned user exists
    def validate_assigned_to(self, value):
        if not User.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Assigned user does not exist.")
        return value
