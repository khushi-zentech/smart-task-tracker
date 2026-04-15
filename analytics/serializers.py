from .models import TimeLog
from rest_framework import serializers

class TimeLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeLog
        fields = ['id', 'task', 'hours_spent', 'description', 'log_date']