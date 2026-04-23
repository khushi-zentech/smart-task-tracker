from tasks.models import Task
from django.db import models
from django.conf import settings

# Create your models here.
User = settings.AUTH_USER_MODEL

class TimeLog(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='time_logs')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    hours_spent = models.FloatField()
    description = models.TextField(blank=True)
    
    log_date = models.DateField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.task} - {self.hours_spent} H"