from rest_framework import serializers
from .models import Project, ProjectMember
from django.contrib.auth import get_user_model

User = get_user_model()

class ProjectSerializer(serializers.ModelSerializer):
    created_by = serializers.ReadOnlyField(source='created_by.username')

    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'workspace', 'created_by', 'created_at']
        
    def validate_workspace(self, workspace):
        if workspace.is_deleted:
            raise serializers.ValidationError("Workspace does not exist for this id!")
        
        return workspace

class ProjectMemberSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(queryset=User.objects.filter(is_deleted=False), slug_field='username')

    class Meta:
        model = ProjectMember
        fields = ['id', 'project', 'user', 'role']