from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, permissions, status

from workspace import constants
from .services import WorkspaceService
from .serializers import WorkspaceSerializer

class WorkspaceViewSet(viewsets.ModelViewSet):
    serializer_class = WorkspaceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = WorkspaceService.get_queryset(self.request.user)
        return queryset

    def create(self, request, *args, **kwargs):
        data, errors = WorkspaceService.create_workspace(request.data, request.user)

        if errors:
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {
                "message": constants.WORKSPACE_CREATED_SUCCESS,
                "data": data
            }, status=status.HTTP_201_CREATED
        )

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        data, error = WorkspaceService.update_workspace(instance, request.user, request.data)

        if error == constants.ONLY_OWNER_UPDATE:
            return Response({"message": constants.ONLY_OWNER_UPDATE}, status=status.HTTP_403_FORBIDDEN)

        if isinstance(error, dict):
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message": constants.WORKSPACE_UPDATED_MESSAGE, "data": data})

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        success, error = WorkspaceService.delete_workspace(instance, request.user)

        if error == constants.ONLY_OWNER_DELETE:
            return Response({"message": constants.ONLY_OWNER_DELETE}, status=status.HTTP_403_FORBIDDEN)
        return Response({"message": constants.WORKSPACE_DELETED_MESSAGE}, status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def add_member(self, request, pk=None):
        instance = self.get_object()
        data, error = WorkspaceService.add_member(instance, request.user, request.data)

        if error == constants.ONLY_OWNER_ADD:
            return Response({"message": constants.ONLY_OWNER_ADD}, status=status.HTTP_403_FORBIDDEN)

        if isinstance(error, dict):
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message": constants.MEMBER_ADDED_SUCCESS, "data": data}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def remove_member(self, request, pk=None):
        instance = self.get_object()
        username = request.data.get('user')
        success, error = WorkspaceService.remove_member(instance, request.user, username)

        if error == constants.ONLY_OWNER_REMOVE:
            return Response({"message": constants.ONLY_OWNER_REMOVE}, status=status.HTTP_403_FORBIDDEN)

        if error == constants.MEMBER_NOT_FOUND:
            return Response({"message": constants.MEMBER_NOT_FOUND}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message": constants.MEMBER_REMOVED_SUCCESS}, status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['get'])
    def members(self, request, pk=None):
        instance = self.get_object()
        data = WorkspaceService.get_members(instance)
        return Response({"message": constants.GET_MEMBER_SUCCESS, "data": data})