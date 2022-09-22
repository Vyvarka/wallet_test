from rest_framework import permissions


class IsOwnerOrAdminReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        print(f'enter in func{self.__class__}')
        if request.method in permissions.SAFE_METHODS:
            print('enter in if')
            return bool(obj == request.user or request.user.is_staff)
        return False
    
    
class IsOwnerWallet(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        print(f'enter in func{self.__class__}')
        if request.method in permissions.SAFE_METHODS:
            print('enter in if')
            return obj.user == request.user
        return False
    

class IsSenderOrReceiverTransaction(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        print(obj.sender.user, obj.receiver.user)
        if request.method in permissions.SAFE_METHODS:
            return bool(
                obj.sender.user == request.user or
                obj.receiver.user == request.user
            )
        return False
    