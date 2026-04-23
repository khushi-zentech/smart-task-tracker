from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

class Workspace(models.Model):
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_workspaces')

    is_deleted = models.BooleanField(default=False)  

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class WorkspaceMember(models.Model):
    ROLE_CHOICES = (
        ('owner', 'Owner'),
        ('member', 'Member'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='members')

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='member')
    is_deleted = models.BooleanField(default=False)   
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'workspace']

    def __str__(self):
        return f"{self.user} - {self.workspace}"