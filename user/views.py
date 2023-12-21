from rest_framework import generics, status
from django.contrib.auth import get_user_model
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.views import APIView

from user.emails import send_otp_to_email
from user.permissions import IsActivateAndAuthenticated
from user.serializers import (
    UserSerializer,
    AuthTokenSerializer,
    UserCreateSerializer,
    VerifyAccountSerializer
)


class UserCreateView(APIView):
    def post(self, request):
        data = request.data
        serializer = UserCreateSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            send_otp_to_email(serializer.data["email"])

            return Response({
                "status": 201,
                "message": "Registration successfully. Check email for verification.",
                "data": serializer.data
            })

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class VerifyOTPView(APIView):
    def post(self, request):
        try:
            data = request.data
            serializer = VerifyAccountSerializer(data=data)

            if serializer.is_valid():
                email = serializer.data.get("email")
                otp = serializer.data.get("otp")

                user = get_user_model().objects.get(email=email)

                if user.otp != otp:
                    return Response(
                        data="Invalid OTP",
                        status=status.HTTP_400_BAD_REQUEST
                    )

                if user.otp == otp:
                    user.is_verified = True
                    user.save()

                    return Response(
                        data=serializer.data,
                        status=status.HTTP_200_OK,
                        headers={"message": "Registration successfully verified"}
                    )

        except get_user_model().DoesNotExist:
            return Response(
                data="User not found",
                status=status.HTTP_400_BAD_REQUEST,
                headers={"message": "User not found"}
            )


class CreateTokenView(ObtainAuthToken):
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
    serializer_class = AuthTokenSerializer


class UserManageView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = (IsActivateAndAuthenticated,)

    def get_object(self):
        return self.request.user
