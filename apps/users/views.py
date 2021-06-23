from rest_framework.generics import GenericAPIView, ListAPIView
from drf_yasg.utils import swagger_auto_schema
from drf_util.decorators import serialize_decorator
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated

from apps.task.models import Task
from apps.users.serializers import (
    UserDetailSerializer,
    TaskCurrentUserSerializer,
    UserListSerializer
)

User = get_user_model()


class UserRegisterView(GenericAPIView):
    @swagger_auto_schema(request_body=UserDetailSerializer)
    @serialize_decorator(UserDetailSerializer)
    def post(self, request):
        validated_data = request.serializer.validated_data

        user = User.objects.create(
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            username=validated_data['username'],
            email=validated_data['email'],
            is_superuser=False,
            is_staff=False,
        )

        user.set_password(validated_data['password'])
        user.save()

        refresh = RefreshToken.for_user(user)

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        })


class UserList(ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserListSerializer
    permission_classes = [IsAuthenticated]


class TaskCurrentUserListView(ListAPIView):
    serializer_class = TaskCurrentUserSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        queryset = Task.objects.filter(assigned_to=request.user)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
