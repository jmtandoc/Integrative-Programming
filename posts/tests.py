from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Post

CustomUser = get_user_model()

class PostPrivacyTests(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username="testuser", password="password")
        self.admin = CustomUser.objects.create_superuser(username="admin", password="password")
        self.private_post = Post.objects.create(title="Private Post", content="Private content", author=self.user, privacy="private")
        self.public_post = Post.objects.create(title="Public Post", content="Public content", author=self.user, privacy="public")

    def test_user_can_see_public_post(self):
        self.client.login(username="testuser", password="password")
        response = self.client.get(f"/posts/{self.public_post.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_cannot_see_private_post(self):
        self.client.login(username="testuser", password="password")
        response = self.client.get(f"/posts/{self.private_post.id}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_see_private_post(self):
        self.client.login(username="admin", password="password")
        response = self.client.get(f"/posts/{self.private_post.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
