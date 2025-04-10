from django.db import models
from django.contrib.auth.models import AbstractUser
# Extending User model to add roles
class CustomUser(AbstractUser):
    ADMIN = 'admin'
    USER = 'user'
    GUEST = 'guest'
    ROLE_CHOICES = [
        (ADMIN, 'Admin'),
        (USER, 'User'),
        (GUEST, 'Guest'),
    ]
    role = models.CharField(max_length=5, choices=ROLE_CHOICES, default=USER)
    def __str__(self):
        return self.username

# Post model with privacy field
class Post(models.Model):
    PRIVACY_CHOICES = [
        ('public', 'Public'),
        ('private', 'Private'),
    ]
    title = models.CharField(max_length=100)
    content = models.TextField()
    privacy = models.CharField(max_length=10, choices=PRIVACY_CHOICES, default='public')
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='posts')
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.title} by {self.author.username}"

# Comment model remains the same
class Comment(models.Model):
    content = models.TextField()
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='comments')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Comment by {self.author.username} on Post {self.post.id}"

# Like model remains the same
class Like(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='likes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ['user', 'post']
    def __str__(self):
        return f"{self.user.username} likes {self.post.title}"
