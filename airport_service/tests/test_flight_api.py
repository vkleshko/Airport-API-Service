import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count, F
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
    Flight
)
from airport_service.serializers import (
    FlightListSerializer,
    FLightDetailSerializer,
    FLightCreateSerializer
)

FLIGHT_URL = reverse("airport_service:flight-list")


def detail_url(flight_id: int):
    return reverse(
        "airport_service:flight-detail", args=[flight_id]
    )


def sample_flight(**params):
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
    defaults = {
        "route": route,
        "airplane": airplane,
        "departure_time": departure_time,
        "arrival_time": departure_time + datetime.timedelta(hours=2)
    }

    defaults.update(params)

    flight = Flight.objects.create(**defaults)
    flight.crew.set((crew1,))
    return flight


class UnauthenticatedFlightApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(FLIGHT_URL)

        self.assertEqual(
            res.status_code, status.HTTP_401_UNAUTHORIZED
        )


class AuthenticatedFlightApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@gmail.com",
            "secret_password"
        )

        self.client.force_authenticate(self.user)

    def test_flight_list(self):
        sample_flight()

        res = self.client.get(FLIGHT_URL)

        flights = Flight.objects.all().annotate(
            available_tickets=F("airplane__rows")
                              * F("airplane__seats_in_rows") - Count("tickets")
        )
        serializer = FlightListSerializer(flights, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_filtering_flight_by_source_and_destination(self):
        source = Airport.objects.create(
            name="test_name",
            closest_big_city="test_city_replica_source"
        )
        destination = Airport.objects.create(
            name="test_name_destination",
            closest_big_city="test_city_replica_destination"
        )
        route = Route.objects.create(
            source=source,
            destination=destination,
            distance=100
        )

        flight1 = sample_flight()
        flight2 = sample_flight(route=route)

        flights = Flight.objects.annotate(
            available_tickets=F("airplane__rows")
                              * F("airplane__seats_in_rows") - Count("tickets")
        )

        res = self.client.get(
            FLIGHT_URL, {
                "from": "test_city_source",
                "to": "test_city_destination"
            }
        )

        serializer1 = FlightListSerializer(
            flights.get(id=flight1.id)
        )
        serializer2 = FlightListSerializer(
            flights.get(id=flight2.id)
        )

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_return_flight_empty_list_when_airplane_departed(self):
        departure_time = timezone.now() - datetime.timedelta(hours=2)
        arrival_time = departure_time + datetime.timedelta(hours=1)

        sample_flight(
            departure_time=departure_time,
            arrival_time=arrival_time
        )

        res = self.client.get(FLIGHT_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 0)

    def test_retrieve_flight_detail(self):
        flight = sample_flight()

        url = detail_url(flight.id)
        res = self.client.get(url)

        serializer = FLightDetailSerializer(flight)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_flight_forbidden(self):
        crew1 = Crew.objects.create(
            first_name="test_first", last_name="test_last"
        )
        crew2 = Crew.objects.create(
            first_name="test_first_2", last_name="test_last_2"
        )
        airplane_type = AirplaneType.objects.create(name="test_type")
        airplane = Airplane.objects.create(
            name="test",
            rows=10,
            seats_in_rows=10,
            airplane_type=airplane_type
        )
        source = Airport.objects.create(
            name="test_source_name",
            closest_big_city="test_city_source"
        )
        destination = Airport.objects.create(
            name="test_destination_name",
            closest_big_city="test_city_destination"
        )
        route = Route.objects.create(
            source=source,
            destination=destination,
            distance=100
        )
        departure_time = timezone.now() + datetime.timedelta(hours=1)
        payload = {
            "route": route.id,
            "airplane": airplane.id,
            "departure_time": departure_time,
            "arrival_time": departure_time + datetime.timedelta(hours=2),
            "crew": (crew1.id, crew2.id)
        }

        res = self.client.post(FLIGHT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminFlightApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@gmail.com",
            "secret_password",
            is_staff=True
        )

        self.client.force_authenticate(self.user)

    def test_create_flight(self):
        crew1 = Crew.objects.create(
            first_name="test_first", last_name="test_last"
        )
        crew2 = Crew.objects.create(
            first_name="test_first_2", last_name="test_last_2"
        )
        airplane_type = AirplaneType.objects.create(name="test_type")
        airplane = Airplane.objects.create(
            name="test",
            rows=10,
            seats_in_rows=10,
            airplane_type=airplane_type
        )
        source = Airport.objects.create(
            name="test_source_name",
            closest_big_city="test_city_source"
        )
        destination = Airport.objects.create(
            name="test_destination_name",
            closest_big_city="test_city_destination"
        )
        route = Route.objects.create(
            source=source,
            destination=destination,
            distance=100
        )
        departure_time = timezone.now() + datetime.timedelta(hours=1)
        payload = {
            "route": route.id,
            "airplane": airplane.id,
            "departure_time": departure_time,
            "arrival_time": departure_time + datetime.timedelta(hours=2),
            "crew": (crew1.id, crew2.id)
        }

        res = self.client.post(FLIGHT_URL, payload)
        flight = Flight.objects.get(id=res.data["id"])
        serializer = FLightCreateSerializer(flight)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        for key in payload:
            self.assertEqual(res.data[key], serializer.data[key])

    def test_create_flight_with_departure_eq_arrival_time_raise_error(self):
        crew1 = Crew.objects.create(
            first_name="test_first", last_name="test_last"
        )
        crew2 = Crew.objects.create(
            first_name="test_first_2", last_name="test_last_2"
        )
        airplane_type = AirplaneType.objects.create(name="test_type")
        airplane = Airplane.objects.create(
            name="test",
            rows=10,
            seats_in_rows=10,
            airplane_type=airplane_type
        )
        source = Airport.objects.create(
            name="test_source_name",
            closest_big_city="test_city_source"
        )
        destination = Airport.objects.create(
            name="test_destination_name",
            closest_big_city="test_city_destination"
        )
        route = Route.objects.create(
            source=source,
            destination=destination,
            distance=100
        )
        departure_time = timezone.now() + datetime.timedelta(hours=1)
        payload = {
            "route": route.id,
            "airplane": airplane.id,
            "departure_time": departure_time,
            "arrival_time": departure_time,
            "crew": (crew1.id, crew2.id)
        }

        res = self.client.post(FLIGHT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_flight_with_departure_lt_arrival_time_raise_error(self):
        crew1 = Crew.objects.create(
            first_name="test_first", last_name="test_last"
        )
        crew2 = Crew.objects.create(
            first_name="test_first_2", last_name="test_last_2"
        )
        airplane_type = AirplaneType.objects.create(name="test_type")
        airplane = Airplane.objects.create(
            name="test",
            rows=10,
            seats_in_rows=10,
            airplane_type=airplane_type
        )
        source = Airport.objects.create(
            name="test_source_name",
            closest_big_city="test_city_source"
        )
        destination = Airport.objects.create(
            name="test_destination_name",
            closest_big_city="test_city_destination"
        )
        route = Route.objects.create(
            source=source,
            destination=destination,
            distance=100
        )
        departure_time = timezone.now() + datetime.timedelta(hours=1)
        payload = {
            "route": route.id,
            "airplane": airplane.id,
            "departure_time": departure_time,
            "arrival_time": departure_time - datetime.timedelta(hours=2),
            "crew": (crew1.id, crew2.id)
        }

        res = self.client.post(FLIGHT_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
