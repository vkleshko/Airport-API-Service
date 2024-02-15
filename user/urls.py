from django.urls import path

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from user.views import (
    UserCreateView,
    UserManageView,
    VerifyOTPView,
)

urlpatterns = [
    path("register/", UserCreateView.as_view(), name="create"),
    path("verify-email/", VerifyOTPView.as_view(), name="verify"),
    path("me/", UserManageView.as_view(), name="manage"),
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),

]

app_name = "user"
