from django.conf.urls import url
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers

from apps.task.views import TaskViewSet
from apps.task.views import CommentViewSet

router = routers.SimpleRouter()
router.register(r'tasks', TaskViewSet)

comments_router = routers.NestedSimpleRouter(router, r'tasks', lookup='task')
comments_router.register(r'comments', CommentViewSet)


urlpatterns = [
    url(r'', include(router.urls)),
    url(r'', include(comments_router.urls)),
]
