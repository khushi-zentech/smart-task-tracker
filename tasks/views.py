from rest_framework.response import Response
from rest_framework import viewsets, permissions, status
from rest_framework.exceptions import ValidationError, NotFound

from .models import Task
from .serializers import TaskSerializer
from projects.models import ProjectMember

# Create your views here.
class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        return Task.objects.filter(
            is_deleted=False,
            project__is_deleted=False,
            project__workspace__is_deleted=False,
            project__workspace__members__user=user,
            project__workspace__members__is_deleted=False
        ).distinct()

    def get_object(self):
        try:
            return self.get_queryset().get(pk=self.kwargs['pk'])
        except Task.DoesNotExist:
            raise NotFound("Task not found or access denied")

    def perform_create(self, serializer):
        project = serializer.validated_data['project']
        user = self.request.user

        if project.is_deleted or project.workspace.is_deleted:
            raise ValidationError("Project does not exist!")

        is_member = ProjectMember.objects.filter(
            project=project,
            user=user,
            is_deleted=False
        ).exists()

        if not is_member:
            raise ValidationError("You are not part of this project")

        assigned_user = serializer.validated_data.get('assigned_to')

        if assigned_user:
            is_project_member = ProjectMember.objects.filter(
                project=project,
                user=assigned_user,
                is_deleted=False
            ).exists()

            if not is_project_member:
                raise ValidationError("Assigned user not in project")

        serializer.save(created_by=user)

    def update(self, request, *args, **kwargs):
        task = self.get_object()
        user = request.user

        if task.created_by == user:
            return super().update(request, *args, **kwargs)
        elif task.assigned_to == user:
            allowed_fields = ['status']

            for field in request.data.keys():
                if field not in allowed_fields:
                    return Response({"error": "You can only update status"}, status=status.HTTP_403_FORBIDDEN)

            return super().update(request, *args, **kwargs)
        return Response({"error": "Not allowed"}, status=403)

    def destroy(self, request, *args, **kwargs):
        task = self.get_object()

        if task.created_by != request.user:
            return Response({"error": "Only creator can delete"}, status=status.HTTP_403_FORBIDDEN)

        task.is_deleted = True
        task.save()
        return Response({"message": "Task deleted"}, status=status.HTTP_204_NO_CONTENT)