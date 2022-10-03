from rest_framework import permissions


class IsOwnerOrAdminReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return bool(obj == request.user or request.user.is_staff)
        return False
    
    
class IsOwnerWallet(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        safe_methods = ['GET', 'DELETE']
        if request.method in safe_methods:
            return bool(obj.user == request.user)
        return False
    

class IsSenderOrReceiverTransaction(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return bool(
                obj.sender.user == request.user or
                obj.receiver.user == request.user
            )
        return False
    