from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from django.test import TestCase
from rest_framework.test import APIClient

from airport_service.models import Airplane, AirplaneType
from airport_service.serializers import (
    AirplaneListSerializer,
    AirplaneDetailSerializer,
    AirplaneCreateSerializer
)

AIRPLANE_URL = reverse("airport_service:airplane-list")


def detail_url(airplane_id: int):
    return reverse("airport_service:airplane-detail", args=[airplane_id])


def sample_airplane(**params):
    airplane_type = AirplaneType.objects.create(name="test_type")
    defaults = {
        "name": "test",
        "rows": 10,
        "seats_in_rows": 10,
        "airplane_type": airplane_type
    }
    defaults.update(params)

    return Airplane.objects.create(**defaults)


class UnauthenticatedAirplaneApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(AIRPLANE_URL)

        self.assertEqual(
            res.status_code, status.HTTP_401_UNAUTHORIZED
        )


class AuthenticatedAirplaneApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@gmail.com",
            "secret_password"
        )

        self.client.force_authenticate(self.user)

    def test_airplane_list(self):
        sample_airplane()
        sample_airplane(name="test1")

        res = self.client.get(AIRPLANE_URL)

        airplanes = Airplane.objects.all()
        serializer = AirplaneListSerializer(airplanes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_retrieve_airplane_detail(self):
        airplane = sample_airplane()

        url = detail_url(airplane.id)
        res = self.client.get(url)

        serializer = AirplaneDetailSerializer(airplane)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_airplane_forbidden(self):
        airplane_type = AirplaneType.objects.create(
            name="test_type"
        )
        payload = {
            "name": "test",
            "rows": 10,
            "seats_in_rows": 10,
            "airplane_type": airplane_type.id
        }

        res = self.client.post(AIRPLANE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminAirplaneApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@gmail.com",
            "secret_password",
            is_staff=True
        )

        self.client.force_authenticate(self.user)

    def test_create_airplane(self):
        airplane_type = AirplaneType.objects.create(
            name="test_type"
        )
        payload = {
            "name": "test",
            "rows": 10,
            "seats_in_rows": 10,
            "airplane_type": airplane_type.id
        }

        res = self.client.post(AIRPLANE_URL, payload)
        airplane = Airplane.objects.get(id=res.data["id"])
        serializer = AirplaneCreateSerializer(airplane)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        for key in payload:
            self.assertEqual(res.data[key], serializer.data[key])

    def test_delete_airplane_not_allowed(self):
        airplane = sample_airplane()

        url = detail_url(airplane.id)
        res = self.client.delete(url)

        self.assertEqual(
            res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED
        )
