from django.contrib.auth import get_user_model
from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated, AllowAny

from apps.users.serializers import UserSerializer, UserListSerializer


User = get_user_model()


class UserViewSet(mixins.ListModelMixin, GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserListSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        """
        Can use __doc__ to add description to endpoints even if they are created using mixins
        """
        return super(UserViewSet, self).list(request, *args, **kwargs)

    @action(methods=['post'], detail=False, url_path='register',
            permission_classes=[AllowAny], serializer_class=UserSerializer)
    def register(self, request, *args, **kwargs):
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


# Todo: remove unused code
