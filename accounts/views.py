from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser

from .models import User
from .serializers import RegisterSerializer, UserSerializer, UpdateProfileSerializer, ChangePasswordSerializer

# Create your views here.
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
        user = self.request.user
        
        if user.is_staff:
            return User.objects.filter(is_deleted=False)
        
        return User.objects.filter(id=user.id, is_deleted=False)

    @action(detail=False, methods=['get'])
    def user_details(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def change_password(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        
        if serializer.is_valid():
            if not request.user.check_password(serializer.validated_data['old_password']):
                return Response({"error": "Old password incorrect"}, status=status.HTTP_400_BAD_REQUEST)

            request.user.set_password(serializer.validated_data['new_password'])
            
            request.user.save()
            return Response({"message": "Password updated successfully"})

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        
        user.is_deleted = True
        user.save()
        
        return Response({"message": "User deleted successfully"}, status=status.HTTP_204_NO_CONTENT)