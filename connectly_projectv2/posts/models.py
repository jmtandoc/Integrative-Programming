from django.db import models


# User model representing system users
class User(models.Model):
    username = models.CharField(max_length=100, unique=True)  # Ensure unique usernames
    email = models.EmailField(unique=True)  # Enforce unique email addresses
    created_at = models.DateTimeField(auto_now_add=True)  # Automatically set creation timestamp

    def __str__(self):
        return self.username

# Post model linked to User through a ForeignKey
class Post(models.Model):
    content = models.CharField(max_length=255)  # Post content with a max length
    author = models.TextField()  # Optional detailed post author

    created_at = models.DateTimeField(auto_now_add=True)  # Automatically set creation timestamp

    def __str__(self):
        return f"Post: {self.content} assigned to {self.assigned_to.username}"
