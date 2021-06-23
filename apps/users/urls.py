from django.urls import path

from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView

from apps.users.views import UserRegisterView, UserList


urlpatterns = [
    path('users/list/', UserList.as_view(), name='users-list'),
    path('user/regiter/', UserRegisterView.as_view(), name='user_register'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
