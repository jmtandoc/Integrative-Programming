from rest_framework import permissions

class IsPostAuthor(permissions.BasePermission):
    """
    Custom permission to only allow the post's author to access/edit it.
    """

    def has_object_permission(self, request, view, obj):
        return obj.author == request.user or request.user.is_staff