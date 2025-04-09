from rest_framework import permissions

class IsPostAuthor(permissions.BasePermission):
    """
    Custom permission to only allow authors of a post to edit or delete it.
    """

    def has_permission(self, request, view):
        # You can check permissions for certain actions here if necessary
        return True

    def has_object_permission(self, request, view, obj):
        # Check if the user is the author of the post
        return obj.author == request.user
