from django.db import IntegrityError
from workspace.models import WorkspaceMember
from projects.models import Project, ProjectMember
from projects.serializers import ProjectSerializer, ProjectMemberSerializer
from projects.constants import (
    PROJECT_NOT_FOUND,
    SOMETHING_WENT_WRONG,
    WORKSPACE_NOT_EXIST,
    NOT_WORKSPACE_MEMBER,
    ONLY_OWNER_UPDATE_MESSAGE,
    ONLY_OWNER_DELETE_MESSAGE,
    MEMBER_NOT_FOUND,
    PROJECT_ID_REQUIRED,
    ONLY_OWNER_ASSIGN,
    ONLY_OWNER_REMOVE,
    USER_NOT_IN_WORKSPACE,
    ALREADY_ASSIGNED_MESSAGE,
    INTEGRITYERROR_MESSAGE,
)

class ProjectService:
    @staticmethod
    def get_projects_queryset(user):
        try:
            return Project.objects.filter(
                is_deleted=False,
                workspace__is_deleted=False,
                workspace__members__user=user,
                workspace__members__is_deleted=False
            ).distinct()
        except Exception:
            return Project.objects.none()

    @staticmethod
    def get_project_object(queryset, pk):
        try:
            return queryset.get(pk=pk), None
        except Project.DoesNotExist:
            return None, PROJECT_NOT_FOUND
        except Exception:
            return None, SOMETHING_WENT_WRONG

    @staticmethod
    def create_project(data, user):
        try:
            serializer = ProjectSerializer(data=data)

            if serializer.is_valid():
                workspace = serializer.validated_data['workspace']
                if workspace.is_deleted:
                    return None, WORKSPACE_NOT_EXIST

                is_member = WorkspaceMember.objects.filter(workspace=workspace, user=user, is_deleted=False).exists()
                if not is_member:
                    return None, NOT_WORKSPACE_MEMBER

                serializer.save(created_by=user)
                return serializer.data, None
            return None, serializer.errors
        except IntegrityError:
            return None, INTEGRITYERROR_MESSAGE
        except Exception:
            return None, SOMETHING_WENT_WRONG

    @staticmethod
    def update_project(instance, user, data):
        try:
            if instance.workspace.owner != user:
                return None, ONLY_OWNER_UPDATE_MESSAGE

            serializer = ProjectSerializer(instance, data=data, partial=True)
            
            if serializer.is_valid():
                serializer.save()
                return serializer.data, None
            return None, serializer.errors
        except Exception:
            return None, SOMETHING_WENT_WRONG

    @staticmethod
    def delete_project(instance, user):
        try:
            if instance.workspace.owner != user:
                return False, ONLY_OWNER_DELETE_MESSAGE

            instance.is_deleted = True
            instance.save()
            return True, None
        except Exception:
            return False, SOMETHING_WENT_WRONG

class ProjectMemberService:
    @staticmethod
    def get_members_queryset(user):
        try:
            return ProjectMember.objects.filter(
                is_deleted=False,
                project__is_deleted=False,
                project__workspace__is_deleted=False,
                project__workspace__members__user=user,
                project__workspace__members__is_deleted=False
            ).distinct()
        except Exception:
            return ProjectMember.objects.none()

    @staticmethod
    def get_member_object(queryset, pk):
        try:
            return queryset.get(pk=pk), None
        except ProjectMember.DoesNotExist:
            return None, MEMBER_NOT_FOUND
        except Exception:
            return None,SOMETHING_WENT_WRONG

    @staticmethod
    def create_member(data, user):
        try:
            project_id = data.get('project')

            if not project_id:
                return None, {"project": PROJECT_ID_REQUIRED}

            try:
                project = Project.objects.get(id=project_id, is_deleted=False)
            except Project.DoesNotExist:
                return None, {"project": PROJECT_NOT_FOUND}

            if project.workspace.is_deleted:
                return None, WORKSPACE_NOT_EXIST

            if project.workspace.owner != user:
                return None, ONLY_OWNER_ASSIGN

            serializer = ProjectMemberSerializer(data=data)

            if serializer.is_valid():
                member_user = serializer.validated_data['user']

                is_workspace_member = WorkspaceMember.objects.filter(
                    workspace=project.workspace,
                    user=member_user,
                    is_deleted=False
                ).exists()

                if not is_workspace_member:
                    return None, USER_NOT_IN_WORKSPACE

                is_project_member = ProjectMember.objects.filter(
                    project=project,
                    user=member_user,
                    is_deleted=False
                ).exists()

                if is_project_member:
                    return None, ALREADY_ASSIGNED_MESSAGE

                serializer.save(project=project)
                return serializer.data, None
            return None, serializer.errors
        except Exception:
            return None, SOMETHING_WENT_WRONG

    @staticmethod
    def update_member(instance, user, data):
        try:
            if instance.project.workspace.owner != user:
                return None, ONLY_OWNER_UPDATE_MESSAGE

            serializer = ProjectMemberSerializer(instance, data=data, partial=True)

            if serializer.is_valid():
                updated_user = serializer.validated_data.get('user', instance.user)

                is_workspace_member = WorkspaceMember.objects.filter(
                    workspace=instance.project.workspace,
                    user=updated_user,
                    is_deleted=False
                ).exists()

                if not is_workspace_member:
                    return None, USER_NOT_IN_WORKSPACE

                serializer.save()
                return serializer.data, None
            return None, serializer.errors
        except Exception:
            return None, SOMETHING_WENT_WRONG

    @staticmethod
    def delete_member(instance, user):
        try:
            if instance.project.workspace.owner != user:
                return False, ONLY_OWNER_REMOVE

            instance.is_deleted = True
            instance.save()
            return True, None
        except Exception:
            return False, SOMETHING_WENT_WRONG