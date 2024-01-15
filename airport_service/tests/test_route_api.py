from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from django.test import TestCase
from rest_framework.test import APIClient

from airport_service.models import Route, Airport
from airport_service.serializers import (
    RouteListSerializer,
    RouteDetailSerializer,
    RouteCreateSerializer
)

ROUTE_URL = reverse("airport_service:route-list")


def detail_url(route_id: int):
    return reverse(
        "airport_service:route-detail", args=[route_id]
    )


def sample_route(**params):
    source = Airport.objects.create(
        name="test_name",
        closest_big_city="test_city_source"
    )
    destination = Airport.objects.create(
        name="test_name",
        closest_big_city="test_city_destination"
    )
    defaults = {
        "source": source,
        "destination": destination,
        "distance": 100
    }
    defaults.update(params)

    return Route.objects.create(**defaults)


class UnauthenticatedRouteApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(ROUTE_URL)

        self.assertEqual(
            res.status_code, status.HTTP_401_UNAUTHORIZED
        )


class AuthenticatedRouteApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@gmail.com",
            "secret_password"
        )

        self.client.force_authenticate(self.user)

    def test_route_list(self):
        sample_route()

        res = self.client.get(ROUTE_URL)

        routes = Route.objects.all()
        serializer = RouteListSerializer(routes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_retrieve_route_detail(self):
        route = sample_route()

        url = detail_url(route.id)
        res = self.client.get(url)

        serializer = RouteDetailSerializer(route)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_route_forbidden(self):
        source = Airport.objects.create(
            name="test_name",
            closest_big_city="test_city_source"
        )
        destination = Airport.objects.create(
            name="test_name",
            closest_big_city="test_city_destination"
        )
        payload = {
            "source": source.id,
            "destination": destination.id,
            "distance": 100
        }

        res = self.client.post(ROUTE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminRouteApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@gmail.com",
            "secret_password",
            is_staff=True
        )

        self.client.force_authenticate(self.user)

    def test_create_route(self):
        source = Airport.objects.create(
            name="test_name",
            closest_big_city="test_city_source"
        )
        destination = Airport.objects.create(
            name="test_name",
            closest_big_city="test_city_destination"
        )
        payload = {
            "source": source.id,
            "destination": destination.id,
            "distance": 100
        }

        res = self.client.post(ROUTE_URL, payload)
        route = Route.objects.get(id=res.data["id"])
        serializer = RouteCreateSerializer(route)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        for key in payload:
            self.assertEqual(res.data[key], serializer.data[key])

    def test_validate_destination(self):
        destination = Airport.objects.create(
            name="test_name",
            closest_big_city="test_city_destination"
        )
        payload = {
            "source": destination.id,
            "destination": destination.id,
            "distance": 100
        }

        res = self.client.post(ROUTE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_route_not_allowed(self):
        route = sample_route()

        url = detail_url(route.id)
        res = self.client.delete(url)

        self.assertEquals(
            res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED
        )
