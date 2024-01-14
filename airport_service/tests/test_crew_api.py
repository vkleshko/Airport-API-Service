from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from django.test import TestCase
from rest_framework.test import APIClient

from airport_service.models import Crew
from airport_service.serializers import CrewSerializer

CREW_URL = reverse("airport_service:crew-list")


def detail_url(crew_id: int):
    return reverse("airport_service:crew-detail", args=[crew_id])


def sample_crew(**params):
    defaults = {
        "first_name": "test",
        "last_name": "test",
    }
    defaults.update(params)

    return Crew.objects.create(**defaults)


class UnauthenticatedCrewApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(CREW_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedCrewApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@gmail.com",
            "secret_password"
        )

        self.client.force_authenticate(self.user)

    def test_crew_list(self):
        sample_crew()
        sample_crew(first_name="test1")

        res = self.client.get(CREW_URL)

        crews = Crew.objects.all()
        serializer = CrewSerializer(crews, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_create_crew_forbidden(self):
        payload = {
            "first_name": "test",
            "last_name": "test1"
        }

        res = self.client.post(CREW_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminCrewApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@gmail.com",
            "secret_password",
            is_staff=True
        )

        self.client.force_authenticate(self.user)

    def test_create_crew(self):
        payload = {
            "first_name": "test",
            "last_name": "test1"
        }

        res = self.client.post(CREW_URL, payload)
        crew = Crew.objects.get(id=res.data["id"])

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        for key in payload:
            self.assertEqual(res.data[key], getattr(crew, key))

    def test_delete_crew_not_allowed(self):
        crew = sample_crew()

        url = detail_url(crew.id)
        res = self.client.delete(url)

        self.assertEquals(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
