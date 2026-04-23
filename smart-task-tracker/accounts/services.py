from .models import User
from .constants import OLD_PASSWORD_INCORRECT
from .serializers import RegisterSerializer, UserSerializer, UpdateProfileSerializer, ChangePasswordSerializer

class UserService:
    @staticmethod
    def get_queryset(user):
        if user.is_staff:
            user = User.objects.filter(is_deleted=False)
            return user
        
        return User.objects.filter(id=user.id, is_deleted=False)

    @staticmethod
    def register(data):
        serializer = RegisterSerializer(data=data)
        
        if serializer.is_valid():
            serializer.save()
            return serializer.data, None
        return None, serializer.errors

    @staticmethod
    def get_user_details(user):
        return UserSerializer(user).data

    @staticmethod
    def update_user(instance, data):
        serializer = UpdateProfileSerializer(instance, data=data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return serializer.data, None
        return None, serializer.errors

    @staticmethod
    def change_password(user, data):
        serializer = ChangePasswordSerializer(data=data)

        if serializer.is_valid():
            if not user.check_password(serializer.validated_data['old_password']):
                return None, OLD_PASSWORD_INCORRECT

            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return True, None

        return None, serializer.errors

    @staticmethod
    def soft_delete(instance):
        instance.is_deleted = True
        instance.save()
        
        return True