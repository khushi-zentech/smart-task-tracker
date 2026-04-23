from rest_framework import serializers
from .models import Workspace, WorkspaceMember
from django.contrib.auth import get_user_model

User = get_user_model()

class WorkspaceSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Workspace
        fields = ['id', 'name', 'owner', 'created_at']

class WorkspaceMemberSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(queryset=User.objects.filter(is_deleted=False), slug_field='username')

    class Meta:
        model = WorkspaceMember
        fields = ['id', 'user', 'role', 'joined_at']