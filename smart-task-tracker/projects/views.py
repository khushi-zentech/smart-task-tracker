from .models import Project, ProjectMember
from workspace.models import WorkspaceMember
from .serializers import ProjectSerializer, ProjectMemberSerializer

from rest_framework.response import Response
from rest_framework import viewsets, permissions, status
from rest_framework.exceptions import NotFound, ValidationError

class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        return Project.objects.filter(
            is_deleted=False,
            workspace__is_deleted=False,
            workspace__members__user=user,
            workspace__members__is_deleted=False
        ).distinct()

    def get_object(self):
        try:
            return self.get_queryset().get(pk=self.kwargs['pk'])
        except Project.DoesNotExist:
            raise NotFound("Project not found or access denied")

    def perform_create(self, serializer):
        workspace = serializer.validated_data['workspace']
        user = self.request.user

        if workspace.is_deleted:
            raise ValidationError("Workspace is deleted")

        is_member = WorkspaceMember.objects.filter(
            workspace=workspace,
            user=user,
            is_deleted=False
        ).exists()

        if not is_member:
            raise ValidationError("You are not a member of this workspace")

        serializer.save(created_by=user)

    def update(self, request, *args, **kwargs):
        project = self.get_object()

        if project.workspace.owner != request.user:
            return Response({"error": "Only owner can update"}, status=status.HTTP_403_FORBIDDEN)

        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        project = self.get_object()

        if project.workspace.owner != request.user:
            return Response({"error": "Only owner can delete"}, status=status.HTTP_403_FORBIDDEN)

        project.is_deleted = True
        project.save()

        return Response({"message": "Project deleted"}, status=status.HTTP_204_NO_CONTENT)

class ProjectMemberViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectMemberSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        return ProjectMember.objects.filter(
            is_deleted=False,
            project__is_deleted=False,
            project__workspace__is_deleted=False,
            project__workspace__members__user=user,
            project__workspace__members__is_deleted=False
        ).distinct()

    def get_object(self):
        try:
            return self.get_queryset().get(pk=self.kwargs['pk'])
        except ProjectMember.DoesNotExist:
            raise NotFound("Project member not found or access denied")

    def create(self, request, *args, **kwargs):
        user = request.user
        project_id = request.data.get('project')

        if not project_id:
            raise ValidationError({"project": "Project ID is required"})

        try:
            project = Project.objects.get(id=project_id, is_deleted=False)
        except Project.DoesNotExist:
            raise ValidationError({"project": "Project not found or deleted"})

        if project.workspace.is_deleted:
            raise ValidationError("Workspace is deleted")

        if project.workspace.owner != user:
            return Response({"error": "Only owner can assign"}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            member_user = serializer.validated_data['user']

            is_workspace_member = WorkspaceMember.objects.filter(workspace=project.workspace, user=member_user, is_deleted=False).exists()

            if not is_workspace_member:
                return Response({"error": "User not in workspace"}, status=status.HTTP_400_BAD_REQUEST)

            is_project_member = ProjectMember.objects.filter(project=project, user=member_user, is_deleted=False).exists()
            
            if is_project_member:
                return Response({"error": "Already assigned"}, status=status.HTTP_400_BAD_REQUEST)

            serializer.save(project=project)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        member = self.get_object()

        if member.project.workspace.owner != request.user:
            return Response({"error": "Only owner can update"}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(member, data=request.data, partial=True)

        if serializer.is_valid():
            updated_user = serializer.validated_data.get('user', member.user)

            is_workspace_member = WorkspaceMember.objects.filter(workspace=member.project.workspace, user=updated_user, is_deleted=False).exists()

            if not is_workspace_member:
                return Response({"error": "User not in workspace"}, status=status.HTTP_400_BAD_REQUEST)

            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        member = self.get_object()

        if member.project.workspace.owner != request.user:
            return Response({"error": "Only owner can remove"}, status=status.HTTP_403_FORBIDDEN)

        member.is_deleted = True
        member.save()

        return Response({"message": "Member removed"}, status=status.HTTP_204_NO_CONTENT)