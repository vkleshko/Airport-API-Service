from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from django.test import TestCase
from rest_framework.test import APIClient

from airport_service.models import AirplaneType
from airport_service.serializers import AirplaneTypeSerializer

AIRPLANE_TYPE_URL = reverse("airport_service:airplanetype-list")


def detail_url(airplane_type_id: int):
    return reverse(
        "airport_service:airplanetype-detail", args=[airplane_type_id]
    )


def sample_airplane_type(**params):
    defaults = {
        "name": "test",
    }
    defaults.update(params)

    return AirplaneType.objects.create(**defaults)


class UnauthenticatedAirplaneTypeApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(AIRPLANE_TYPE_URL)

        self.assertEqual(
            res.status_code, status.HTTP_401_UNAUTHORIZED
        )


class AuthenticatedAirplaneTypeApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@gmail.com",
            "secret_password"
        )

        self.client.force_authenticate(self.user)

    def test_airplane_type_list(self):
        sample_airplane_type()
        sample_airplane_type(name="test1")

        res = self.client.get(AIRPLANE_TYPE_URL)

        airplane_types = AirplaneType.objects.all()
        serializer = AirplaneTypeSerializer(airplane_types, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_create_airplane_type_forbidden(self):
        payload = {
            "name": "test",
        }

        res = self.client.post(AIRPLANE_TYPE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminAirplaneTypeApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@gmail.com",
            "secret_password",
            is_staff=True
        )

        self.client.force_authenticate(self.user)

    def test_create_airplane_type(self):
        payload = {
            "name": "test",
        }

        res = self.client.post(AIRPLANE_TYPE_URL, payload)
        airplane_type = AirplaneType.objects.get(id=res.data["id"])

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        for key in payload:
            self.assertEqual(res.data[key], getattr(airplane_type, key))

    def test_delete_airplane_type_not_allowed(self):
        airplane_type = sample_airplane_type()

        url = detail_url(airplane_type.id)
        res = self.client.delete(url)

        self.assertEquals(
            res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED
        )
