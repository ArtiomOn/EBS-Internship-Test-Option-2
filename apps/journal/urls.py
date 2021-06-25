from django.conf.urls import url
from django.urls import include
from rest_framework_nested import routers

from apps.journal.views import TimerViewSet
from apps.tasks.views import TaskViewSet

tasks_router = routers.SimpleRouter()
tasks_router.register(r'tasks', TaskViewSet)

timers_router = routers.NestedSimpleRouter(tasks_router, r'tasks', lookup='task')
timers_router.register(r'timers', TimerViewSet)

urlpatterns = [
    url(r'', include(timers_router.urls)),
]
