from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action

from .models import Workspace, WorkspaceMember
from .serializers import WorkspaceSerializer, WorkspaceMemberSerializer

class WorkspaceViewSet(viewsets.ModelViewSet):
    serializer_class = WorkspaceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        return Workspace.objects.filter(
            is_deleted=False,
            members__user=user,
            members__is_deleted=False
        ).distinct()

    def perform_create(self, serializer):
        workspace = serializer.save(owner=self.request.user)

        WorkspaceMember.objects.create(
            user=self.request.user,
            workspace=workspace,
            role='owner'
        )

    def update(self, request, *args, **kwargs):
        workspace = self.get_object()

        if workspace.owner != request.user:
            return Response({"error": "Only owner can update!"}, status=status.HTTP_403_FORBIDDEN)

        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        workspace = self.get_object()

        if workspace.owner != request.user:
            return Response({"error": "Only owner can delete!"}, status=status.HTTP_403_FORBIDDEN)

        workspace.is_deleted = True
        workspace.save()
        
        WorkspaceMember.objects.filter(workspace=workspace).update(is_deleted=True)

        return Response({"message": "Workspace deleted Successfully"}, status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def add_member(self, request, pk=None):
        workspace = self.get_object()

        if workspace.owner != request.user:
            return Response({"error": "Only owner can add members!"}, status=status.HTTP_403_FORBIDDEN)

        serializer = WorkspaceMemberSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(workspace=workspace)
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def remove_member(self, request, pk=None):
        workspace = self.get_object()

        if workspace.owner != request.user:
            return Response({"error": "Only owner can remove members!"}, status=status.HTTP_403_FORBIDDEN)

        username = request.data.get('user')

        try:
            member = WorkspaceMember.objects.get(workspace=workspace, user__username=username, is_deleted=False)
            
            member.is_deleted = True
            member.save()

            return Response({"message": "Member removed Successfully."})
        except WorkspaceMember.DoesNotExist:
            return Response({"error": "User not found!"}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def members(self, request, pk=None):
        workspace = self.get_object()
        members = WorkspaceMember.objects.filter(workspace=workspace, is_deleted=False)

        serializer = WorkspaceMemberSerializer(members, many=True)
        return Response(serializer.data)