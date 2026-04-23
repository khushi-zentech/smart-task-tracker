from django.urls import path, include
from .views import ProjectViewSet, ProjectMemberViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'project-members', ProjectMemberViewSet, basename='project-member')

urlpatterns = [
    path('', include(router.urls)),
]