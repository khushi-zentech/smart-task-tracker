from django.urls import path, include
from .views import WorkspaceViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'workspaces', WorkspaceViewSet, basename='workspace')

urlpatterns = [
    path('', include(router.urls)),
]