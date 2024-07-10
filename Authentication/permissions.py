from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework import permissions

class IsAdminOrReadOnly(BasePermission):
    """
    Allows access only to authenticated users:
        Admin can create, update, and delete data.
        Users can only read data.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return IsAuthenticated().has_permission(request, view)
        else:
            return request.user.is_staff
        
class AdminUpdateOnly(BasePermission):
    """
    Allows access only to authenticated users:
        Admin can only update data.
        Users can read, create and delete data.
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        if request.user.is_staff:
            return True
        
        return request.method in ['GET', 'POST', 'DELETE']