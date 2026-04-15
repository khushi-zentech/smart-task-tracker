from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework import viewsets, permissions, status

from datetime import timedelta
from django.db.models import Sum
from django.utils.timezone import now

from .models import TimeLog
from .serializers import TimeLogSerializer

from tasks.models import Task
from projects.models import ProjectMember

class AnalyticsViewSet(viewsets.ModelViewSet):
    queryset = TimeLog.objects.filter(is_deleted=False)
    serializer_class = TimeLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return TimeLog.objects.filter(user=self.request.user, is_deleted=False)

    def perform_create(self, serializer):
        user = self.request.user
        task = serializer.validated_data['task']

        if task.is_deleted or task.project.is_deleted:
            raise ValidationError("Invalid task")

        is_member = ProjectMember.objects.filter(project=task.project, user=user, is_deleted=False).exists()

        if not is_member:
            raise ValidationError("You are not part of this project")

        serializer.save(user=user)

    def destroy(self, request, *args, **kwargs):
        log = self.get_object()
        
        log.is_deleted = True
        log.save()
        
        return Response({"message": "Time log deleted"}, status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['get'])
    def total_time(self, request, pk=None):
        try:
            task = Task.objects.get(id=pk, is_deleted=False)
        except Task.DoesNotExist:
            raise ValidationError("Task not found")

        total_time = TimeLog.objects.filter(task=task, is_deleted=False).aggregate(total=Sum('hours_spent'))['total'] or 0

        return Response({"task_id": task.id, "total_time": total_time}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def user_stats(self, request):
        user = request.user

        total_tasks = Task.objects.filter(assigned_to=user, is_deleted=False).count()
        completed_tasks = Task.objects.filter(assigned_to=user, status='done', is_deleted=False).count()
        total_time = TimeLog.objects.filter(user=user, is_deleted=False).aggregate(total=Sum('hours_spent'))['total'] or 0
        
        if total_tasks > 0:
            productivity_score = ((completed_tasks / total_tasks) * 100) + total_time 
        else:
            productivity_score = total_time 

        return Response(
            {
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "total_time": total_time,
                "productivity_score": productivity_score
            }, status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['get'])
    def weekly_report(self, request):
        user = request.user
        week_ago = now() - timedelta(days=7)

        completed = Task.objects.filter(
            assigned_to=user,
            status='done',
            created_at__gte=week_ago,
            is_deleted=False
        ).count()

        time_spent = TimeLog.objects.filter(
            user=user,
            created_at__gte=week_ago,
            is_deleted=False
        ).aggregate(total=Sum('hours_spent'))['total'] or 0

        return Response(
            {
                "weekly_completed_tasks": completed,
                "weekly_time_spent": time_spent
            }, status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['get'])
    def monthly_report(self, request):
        user = request.user
        month_ago = now() - timedelta(days=30)

        completed = Task.objects.filter(
            assigned_to=user,
            status='done',
            created_at__gte=month_ago,
            is_deleted=False
        ).count()

        time_spent = TimeLog.objects.filter(
            user=user,
            created_at__gte=month_ago,
            is_deleted=False
        ).aggregate(total=Sum('hours_spent'))['total'] or 0

        return Response(
            {
                "monthly_completed_tasks": completed,
                "monthly_time_spent": time_spent
            }, status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['get'])
    def overdue_tasks(self, request):
        tasks = Task.objects.filter(
            assigned_to=request.user,
            deadline__lt=now(),
            status__in=['todo', 'in_progress'],
            is_deleted=False
        )
        
        data = [
            {
                "id": task.id,
                "title": task.title,
                "deadline": task.deadline
            } for task in tasks
        ]
        
        return Response(data)