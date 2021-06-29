from django.conf.urls import url
from django.urls import include
from rest_framework_nested import routers

from apps.journal.views import TimerViewSet, TimeLogViewSet
from apps.tasks.views import TaskViewSet

tasks_router = routers.SimpleRouter()
tasks_router.register(r'tasks', TaskViewSet)

timer_log_router = routers.SimpleRouter()
timer_log_router.register(r'timelogs', TimeLogViewSet)

timer_router = routers.NestedSimpleRouter(tasks_router, r'tasks', lookup='task')
timer_router.register(r'timelog', TimerViewSet)

urlpatterns = [
    url('', include(timer_router.urls)),
    url('', include(timer_log_router.urls))
]
