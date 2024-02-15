from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from airport_service.models import Airport
from airport_service.serializers import AirportSerializer

AIRPORT_URL = reverse("airport_service:airport-list")


def detail_url(airport_id: int):
    return reverse(
        "airport_service:airport-detail", args=[airport_id]
    )


def sample_airport(**params):
    defaults = {
        "name": "test_name",
        "closest_big_city": "test_city"
    }
    defaults.update(params)

    return Airport.objects.create(**defaults)


class UnauthenticatedAirportApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(AIRPORT_URL)

        self.assertEqual(
            res.status_code, status.HTTP_401_UNAUTHORIZED
        )


class AuthenticatedAirportApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@gmail.com",
            "secret_password"
        )

        self.client.force_authenticate(self.user)

    def test_airport_list(self):
        sample_airport()
        sample_airport(name="test_name2")

        res = self.client.get(AIRPORT_URL)

        airports = Airport.objects.all()
        serializer = AirportSerializer(airports, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_filtering_airport_by_name(self):
        airport1 = sample_airport()
        airport2 = sample_airport(
            name="test_name_2",
            closest_big_city="test_city"
        )

        res = self.client.get(AIRPORT_URL, {"name": "test_name_2"})

        serializer1 = AirportSerializer(airport1)
        serializer2 = AirportSerializer(airport2)

        self.assertIn(serializer2.data, res.data["results"])
        self.assertNotIn(serializer1.data, res.data["results"])

    def test_create_airport_forbidden(self):
        payload = {
            "name": "test_name",
            "closest_big_city": "test_city"
        }

        res = self.client.post(AIRPORT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminAirportApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@gmail.com",
            "secret_password",
            is_staff=True
        )

        self.client.force_authenticate(self.user)

    def test_create_airport(self):
        payload = {
            "name": "test_name",
            "closest_big_city": "test_city"
        }

        res = self.client.post(AIRPORT_URL, payload)
        airport = Airport.objects.get(id=res.data["id"])

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        for key in payload:
            self.assertEqual(res.data[key], getattr(airport, key))

    def test_create_same_airport_raises_error(self):
        payload = {
            "name": "test_name",
            "closest_big_city": "test_city"
        }

        res_1 = self.client.post(AIRPORT_URL, payload)
        res_2 = self.client.post(AIRPORT_URL, payload)

        self.assertEqual(res_1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res_2.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_airport_not_allowed(self):
        airport = sample_airport()

        url = detail_url(airport.id)
        res = self.client.delete(url)

        self.assertEquals(
            res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED
        )
