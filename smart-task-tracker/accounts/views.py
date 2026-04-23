from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser

from .models import User
from .serializers import RegisterSerializer, UserSerializer, UpdateProfileSerializer
from .services import UserService
from .constants import (
    USER_REGISTERED_MESSAGE,
    USER_RETRIVED_MESSAGE,
    USER_UPDATE_MESSAGE,
    USER_DELETE_MESSAGE,
    USER_PASSWORD_CHANGE_MESSAGE,
    OLD_PASSWORD_INCORRECT
)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.filter(is_deleted=False)
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action in ['create']:
            return [AllowAny()]
        elif self.action in ['list']:
            return [IsAdminUser()]
        
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == 'create':
            return RegisterSerializer
        elif self.action in ['update', 'partial_update']:
            return UpdateProfileSerializer
        return UserSerializer

    def get_queryset(self):
        queryset = UserService.get_queryset(self.request.user)
        return queryset

    def create(self, request, *args, **kwargs):
        data, errors = UserService.register(request.data)

        if errors:
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {
                "message": USER_REGISTERED_MESSAGE,
                "data": data
            }, status=status.HTTP_201_CREATED    
        )

    @action(detail=False, methods=['get'])
    def details(self, request):
        data = UserService.get_user_details(request.user)

        return Response(
            {
                "message": USER_RETRIVED_MESSAGE,
                "data": data
            }
        )

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        data, errors = UserService.update_user(instance, request.data)

        if errors:
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {
                "message": USER_UPDATE_MESSAGE,
                "data": data
            }
        )

    @action(detail=False, methods=['post'])
    def change_password(self, request):
        result, error = UserService.change_password(request.user, request.data)

        if error == OLD_PASSWORD_INCORRECT:
            return Response(
                {
                    "message": OLD_PASSWORD_INCORRECT
                }, status=status.HTTP_400_BAD_REQUEST
            )

        if isinstance(error, dict):
            return Response(error, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": USER_PASSWORD_CHANGE_MESSAGE}, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        UserService.soft_delete(instance)
        return Response({"message": USER_DELETE_MESSAGE}, status=status.HTTP_204_NO_CONTENT)