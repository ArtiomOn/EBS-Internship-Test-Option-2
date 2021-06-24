from django.conf.urls import url
from django.urls import include, path
from rest_framework_nested import routers

from apps.task.views import TaskViewSet, TaskFilterListView
from apps.task.views import CommentViewSet

router = routers.SimpleRouter()
router.register(r'tasks', TaskViewSet)


comments_list_router = routers.NestedSimpleRouter(router, r'tasks', lookup='task')
comments_list_router.register(r'comments', CommentViewSet)


urlpatterns = [
    path('tasks/search/', TaskFilterListView.as_view()),
    url(r'', include(router.urls)),
    url(r'', include(comments_list_router.urls)),
]
