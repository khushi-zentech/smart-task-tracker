from django.db import models
from django.conf import settings
from workspace.models import Workspace

# Create your models here.
User = settings.AUTH_USER_MODEL

class Project(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='projects')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_projects')
    is_deleted = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
class ProjectMember(models.Model):
    ROLE_CHOICES = (
        ('manager', 'Manager'),
        ('developer', 'Developer'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='members')

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='developer')

    is_deleted = models.BooleanField(default=False)

    assigned_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'project']

    def __str__(self):
        return f"{self.user} - {self.project}"