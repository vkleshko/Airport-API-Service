import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from django.test import TestCase
from rest_framework.test import APIClient

from airport_service.models import (
    AirplaneType,
    Airplane,
    Crew,
    Airport,
    Route,
    Flight,
    Ticket,
    Order
)
from airport_service.serializers import (
    OrderListSerializer,
    OrderDetailSerializer,
    OrderCreateSerializer
)

ORDER_URL = reverse("airport_service:order-list")


def detail_url(order_id: int):
    return reverse(
        "airport_service:order-detail", args=[order_id]
    )


def sample_order(**params):
    try:
        crew1 = Crew.objects.get(id=1)
        source = Airport.objects.get(id=1)
        destination = Airport.objects.get(id=2)
    except ObjectDoesNotExist:
        crew1 = Crew.objects.create(
            first_name="test_first", last_name="test_last"
        )
        source = Airport.objects.create(
            name="test_source_name",
            closest_big_city="test_city_source"
        )
        destination = Airport.objects.create(
            name="test_destination_name",
            closest_big_city="test_city_destination"
        )
    airplane_type = AirplaneType.objects.create(name="test_type")
    airplane = Airplane.objects.create(
        name="test",
        rows=10,
        seats_in_rows=10,
        airplane_type=airplane_type
    )
    route = Route.objects.create(
        source=source,
        destination=destination,
        distance=100
    )
    departure_time = timezone.now() + datetime.timedelta(hours=1)

    flight = Flight.objects.create(
        route=route,
        airplane=airplane,
        departure_time=departure_time,
        arrival_time=departure_time + datetime.timedelta(hours=2)
    )
    flight.crew.set((crew1,))

    order = Order.objects.create(user=params["user"])

    defaults = {
        "row": 2,
        "seat": 2,
        "flight": flight,
        "order": order
    }
    params.__delitem__("user")
    defaults.update(params)
    Ticket.objects.create(**defaults)

    return order


class UnauthenticatedOrderApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(ORDER_URL)

        self.assertEqual(
            res.status_code, status.HTTP_401_UNAUTHORIZED
        )


class AuthenticatedOrderApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@gmail.com",
            "secret_password"
        )

        self.client.force_authenticate(self.user)

    def test_order_list(self):
        sample_order(user=self.user)

        res = self.client.get(ORDER_URL)

        orders = Order.objects.all()
        serializer = OrderListSerializer(orders, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_list_only_owner_orders(self):
        order_1 = sample_order(user=self.user)
        order_2 = sample_order(user=self.user, row=3, seat=3)
        user = get_user_model().objects.create_user(
            "user@gmail.com",
            "secret_password"
        )
        order_3 = sample_order(user=user)

        res = self.client.get(ORDER_URL)

        serializer_1 = OrderListSerializer(order_1)
        serializer_2 = OrderListSerializer(order_2)
        serializer_3 = OrderListSerializer(order_3)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(serializer_1.data, res.data["results"])
        self.assertIn(serializer_2.data, res.data["results"])
        self.assertNotIn(serializer_3.data, res.data["results"])

    def test_retrieve_order_detail(self):
        order = sample_order(user=self.user)

        url = detail_url(order.id)
        res = self.client.get(url)

        serializer = OrderDetailSerializer(order)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_user_create_order_available(self):
        crew1 = Crew.objects.create(
            first_name="test_first", last_name="test_last"
        )
        source = Airport.objects.create(
            name="test_source_name",
            closest_big_city="test_city_source"
        )
        destination = Airport.objects.create(
            name="test_destination_name",
            closest_big_city="test_city_destination"
        )
        airplane_type = AirplaneType.objects.create(name="test_type")
        airplane = Airplane.objects.create(
            name="test",
            rows=10,
            seats_in_rows=10,
            airplane_type=airplane_type
        )
        route = Route.objects.create(
            source=source,
            destination=destination,
            distance=100
        )
        departure_time = timezone.now() + datetime.timedelta(hours=1)

        flight = Flight.objects.create(
            route=route,
            airplane=airplane,
            departure_time=departure_time,
            arrival_time=departure_time + datetime.timedelta(hours=2)
        )
        flight.crew.set((crew1,))

        payload = {
            "tickets": [
                {
                    "row": 2,
                    "seat": 2,
                    "flight": 1,
                }
            ]
        }

        res = self.client.post(ORDER_URL, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)


class AdminOrderApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@gmail.com",
            "secret_password",
            is_staff=True
        )

        self.client.force_authenticate(self.user)

    def test_create_order(self):
        crew1 = Crew.objects.create(
            first_name="test_first", last_name="test_last"
        )
        source = Airport.objects.create(
            name="test_source_name",
            closest_big_city="test_city_source"
        )
        destination = Airport.objects.create(
            name="test_destination_name",
            closest_big_city="test_city_destination"
        )
        airplane_type = AirplaneType.objects.create(name="test_type")
        airplane = Airplane.objects.create(
            name="test",
            rows=10,
            seats_in_rows=10,
            airplane_type=airplane_type
        )
        route = Route.objects.create(
            source=source,
            destination=destination,
            distance=100
        )
        departure_time = timezone.now() + datetime.timedelta(hours=1)

        flight = Flight.objects.create(
            route=route,
            airplane=airplane,
            departure_time=departure_time,
            arrival_time=departure_time + datetime.timedelta(hours=2)
        )
        flight.crew.set((crew1,))

        payload = {
            "tickets": [
                {
                    "row": 2,
                    "seat": 2,
                    "flight": 1,
                }
            ]
        }

        res = self.client.post(ORDER_URL, payload, format="json")
        order = Order.objects.get(id=res.data["id"])
        serializer = OrderCreateSerializer(order)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        for key in payload:
            self.assertEqual(res.data[key], serializer.data[key])

    def test_delete_order_not_allowed(self):
        order = sample_order(user=self.user)

        url = detail_url(order.id)
        res = self.client.delete(url)

        self.assertEquals(
            res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED
        )
