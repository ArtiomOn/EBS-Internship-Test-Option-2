from django.conf.urls import url
from django.urls import include
from rest_framework_nested import routers

from apps.tasks.views import TaskViewSet, CommentViewSet, TimeLogViewSet, TimerViewSet

tasks_router = routers.SimpleRouter()
tasks_router.register(r'tasks', TaskViewSet)

comments_router = routers.NestedSimpleRouter(tasks_router, r'tasks', lookup='task')
comments_router.register(r'comments', CommentViewSet)

timer_log_router = routers.SimpleRouter()
timer_log_router.register(r'timelogs', TimeLogViewSet)

timer_router = routers.NestedSimpleRouter(tasks_router, r'tasks', lookup='task')
timer_router.register(r'timelog', TimerViewSet)

urlpatterns = [
    url(r'', include(tasks_router.urls)),
    url(r'', include(comments_router.urls)),
    url('', include(timer_router.urls)),
    url('', include(timer_log_router.urls))

]
