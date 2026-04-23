from .models import Workspace, WorkspaceMember
from .serializers import WorkspaceSerializer, WorkspaceMemberSerializer
from .constants import ONLY_OWNER_UPDATE, ONLY_OWNER_DELETE, ONLY_OWNER_ADD, ONLY_OWNER_REMOVE, MEMBER_NOT_FOUND

class WorkspaceService:
    @staticmethod
    def get_queryset(user):
        queryset = Workspace.objects.filter(is_deleted=False, members__user=user, members__is_deleted=False).distinct()
        return queryset

    @staticmethod
    def create_workspace(data, user):
        serializer = WorkspaceSerializer(data=data)

        if serializer.is_valid():
            workspace = serializer.save(owner=user)
            WorkspaceMember.objects.create(user=user, workspace=workspace, role='owner')
            return serializer.data, None
        return None, serializer.errors

    @staticmethod
    def update_workspace(instance, user, data):
        if instance.owner != user:
            return None, ONLY_OWNER_UPDATE

        serializer = WorkspaceSerializer(instance, data=data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return serializer.data, None
        return None, serializer.errors

    @staticmethod
    def delete_workspace(instance, user):
        if instance.owner != user:
            return False, ONLY_OWNER_DELETE

        instance.is_deleted = True
        instance.save()
        
        WorkspaceMember.objects.filter(workspace=instance).update(is_deleted=True)
        return True, None

    @staticmethod
    def add_member(instance, user, data):
        if instance.owner != user:
            return None, ONLY_OWNER_ADD

        serializer = WorkspaceMemberSerializer(data=data)

        if serializer.is_valid():
            serializer.save(workspace=instance)
            return serializer.data, None
        return None, serializer.errors

    @staticmethod
    def remove_member(instance, user, username):
        if instance.owner != user:
            return False, ONLY_OWNER_REMOVE

        try:
            member = WorkspaceMember.objects.get(workspace=instance, user__username=username, is_deleted=False)
            member.is_deleted = True
            
            member.save()
            return True, None
        except WorkspaceMember.DoesNotExist:
            return False, MEMBER_NOT_FOUND

    @staticmethod
    def get_members(instance):
        members = WorkspaceMember.objects.filter(workspace=instance, is_deleted=False)
        data = WorkspaceMemberSerializer(members, many=True).data
        
        return data