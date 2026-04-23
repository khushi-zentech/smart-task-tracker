from rest_framework import serializers
from .models import Task
from django.contrib.auth import get_user_model

User = get_user_model()

class TaskSerializer(serializers.ModelSerializer):
    assigned_to = serializers.SlugRelatedField(
        queryset=User.objects.filter(is_deleted=False),
        slug_field='username',
        required=False
    )

    created_by = serializers.ReadOnlyField(source='created_by.username')

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'project',
            'assigned_to', 'status', 'priority',
            'deadline', 'created_by', 'created_at', 'updated_at',
        ]
        
    def validate(self, data):
        instance = self.instance

        if instance:
            old_status = instance.status
            new_status = data.get('status', old_status)

            valid_transitions = {
                'todo': ['in_progress'],
                'in_progress': ['done'],
                'done': []
            }

            if new_status != old_status:
                if new_status not in valid_transitions.get(old_status, []):
                    raise serializers.ValidationError(f"Invalid status transition from {old_status} to {new_status}")
        return data