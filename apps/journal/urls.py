from django.conf.urls import url
from django.urls import include
from rest_framework_nested import routers

from apps.journal.views import TimerViewSet
from apps.tasks.views import TaskViewSet

tasks_router = routers.SimpleRouter()
tasks_router.register(r'tasks', TaskViewSet)

timelog_router = routers.NestedSimpleRouter(tasks_router, r'tasks', lookup='task')
timelog_router.register(r'timelog', TimerViewSet)

urlpatterns = [
    url('', include(timelog_router.urls))
]
