from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .constants import *
from .serializers import ProjectSerializer, ProjectMemberSerializer
from .services.project_services import ProjectService, ProjectMemberService

class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = ProjectService.get_projects_queryset(self.request.user)
        return queryset

    def get_object(self):
        obj, error = ProjectService.get_project_object(self.get_queryset(), self.kwargs['pk'])

        if error:
            return Response({"message": PROJECT_NOT_FOUND}, status=status.HTTP_404_NOT_FOUND)
        return obj

    def create(self, request, *args, **kwargs):
        data, error = ProjectService.create_project(request.data, request.user)

        if isinstance(error, dict):
            return Response(error, status=status.HTTP_400_BAD_REQUEST)

        if error == WORKSPACE_NOT_EXIST:
            return Response({"message": WORKSPACE_NOT_EXIST}, status=status.HTTP_400_BAD_REQUEST)

        if error == NOT_WORKSPACE_MEMBER:
            return Response({"message": NOT_WORKSPACE_MEMBER}, status=status.HTTP_403_FORBIDDEN)

        if error:
            return Response({"message": SOMETHING_WENT_WRONG}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({"message": PROJECT_CREATED_SUCCESS, "data": data}, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        if isinstance(instance, Response):
            return instance

        data, error = ProjectService.update_project(instance, request.user, request.data)

        if error == ONLY_OWNER_UPDATE_MESSAGE:
            return Response({"message": ONLY_OWNER_UPDATE_MESSAGE}, status=status.HTTP_403_FORBIDDEN)

        if isinstance(error, dict):
            return Response(error, status=status.HTTP_400_BAD_REQUEST)

        if error:
            return Response({"message": SOMETHING_WENT_WRONG}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({"message": PROJECT_UPDATED_MESSAGE, "data": data})

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        if isinstance(instance, Response):
            return instance

        success, error = ProjectService.delete_project(instance, request.user)

        if error == ONLY_OWNER_DELETE_MESSAGE:
            return Response({"message": ONLY_OWNER_DELETE_MESSAGE}, status=status.HTTP_403_FORBIDDEN)

        if error:
            return Response({"message": SOMETHING_WENT_WRONG}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({"message": PROJECT_DELETED_MESSAGE}, status=status.HTTP_204_NO_CONTENT)

class ProjectMemberViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ProjectMemberSerializer

    def get_queryset(self):
        queryset = ProjectMemberService.get_members_queryset(self.request.user) 
        return queryset

    def get_object(self):
        obj, error = ProjectMemberService.get_member_object(self.get_queryset(), self.kwargs['pk'])

        if error:
            return Response({"message": MEMBER_NOT_FOUND}, status=status.HTTP_400_BAD_REQUEST)
        return obj

    def create(self, request, *args, **kwargs):
        data, error = ProjectMemberService.create_member(request.data, request.user)

        if isinstance(error, dict):
            return Response(error, status=400)

        if error == WORKSPACE_NOT_EXIST:
            return Response({"message": WORKSPACE_NOT_EXIST}, status=status.HTTP_400_BAD_REQUEST)

        if error == ONLY_OWNER_ASSIGN:
            return Response({"message": ONLY_OWNER_ASSIGN}, status=status.HTTP_403_FORBIDDEN)

        if error == USER_NOT_IN_WORKSPACE:
            return Response({"message": USER_NOT_IN_WORKSPACE}, status=status.HTTP_400_BAD_REQUEST)

        if error == ALREADY_ASSIGNED_MESSAGE:
            return Response({"message": ALREADY_ASSIGNED_MESSAGE}, status=status.HTTP_400_BAD_REQUEST)

        if error:
            return Response({"message": SOMETHING_WENT_WRONG}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({"message": MEMBER_CREATED_SUCCESS, "data": data}, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        if isinstance(instance, Response):
            return instance

        data, error = ProjectMemberService.update_member(instance, request.user, request.data)

        if error == ONLY_OWNER_UPDATE_MESSAGE:
            return Response({"message": ONLY_OWNER_UPDATE_MESSAGE}, status=status.HTTP_403_FORBIDDEN)

        if error == USER_NOT_IN_WORKSPACE:
            return Response({"message": USER_NOT_IN_WORKSPACE}, status=status.HTTP_400_BAD_REQUEST)

        if isinstance(error, dict):
            return Response(error, status=status.HTTP_400_BAD_REQUEST)

        if error:
            return Response({"message": SOMETHING_WENT_WRONG}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({"message": MEMBER_UPDATED_MESSAGE, "data": data})

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        if isinstance(instance, Response):
            return instance

        success, error = ProjectMemberService.delete_member(instance, request.user)

        if error == ONLY_OWNER_REMOVE:
            return Response({"message": ONLY_OWNER_REMOVE}, status=status.HTTP_403_FORBIDDEN)

        if error:
            return Response({"message": SOMETHING_WENT_WRONG}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"message": MEMBER_DELETED_MESSAGE}, status=status.HTTP_204_NO_CONTENT)