from django.urls import include, path
from rest_framework_nested import routers

from apps.tasks.views import TaskViewSet, TaskCommentViewSet, TimeLogViewSet, TaskTimeLogViewSet


base_router = routers.SimpleRouter()
base_router.register(r'tasks', TaskViewSet)
base_router.register(r'timelogs', TimeLogViewSet)

task_router = routers.NestedSimpleRouter(base_router, r'tasks', lookup='task')
task_router.register(r'comments', TaskCommentViewSet)
task_router.register(r'timelogs', TaskTimeLogViewSet)

urlpatterns = [
    path('', include(base_router.urls)),
    path('', include(task_router.urls)),
]
