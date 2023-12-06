from datetime import datetime

from django.db.models import Value
from django.db.models.functions import Concat
from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from airport_service.models import (
    Crew,
    Airport,
    Route,
    AirplaneType,
    Airplane,
    Flight,
    Order,
)
from airport_service.serializers import (
    CrewSerializer,
    AirportSerializer,
    RouteListSerializer,
    RouteCreateSerializer,
    RouteDetailSerializer,
    AirplaneTypeSerializer,
    AirplaneListSerializer,
    AirplaneCreateSerializer,
    AirplaneDetailSerializer,
    FlightListSerializer,
    FLightCreateSerializer,
    FLightDetailSerializer,
    OrderCreateSerializer,
    OrderListSerializer,
    OrderDetailSerializer,

)


class CrewViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    GenericViewSet
):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer

    def get_queryset(self):
        queryset = self.queryset

        full_name = self.request.query_params.get("full_name")
        if full_name:
            queryset = queryset.annotate(
                full_name=Concat("first_name", Value(" "), "last_name")
            )

            queryset = queryset.filter(full_name__icontains=full_name)

        return queryset


class AirportViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    GenericViewSet
):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer

    def get_queryset(self):
        queryset = self.queryset

        name = self.request.query_params.get("name")
        if name:
            queryset = queryset.filter(name__icontains=name)

        return queryset


class RouteViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    GenericViewSet
):
    queryset = Route.objects.select_related(
        "source", "destination"
    )

    def get_queryset(self):
        queryset = self.queryset

        from_ = self.request.query_params.get("from")
        to = self.request.query_params.get("to")

        if from_:
            queryset = queryset.filter(source__name__icontains=from_)

        if to:
            queryset = queryset.filter(destination__name__icontains=to)

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return RouteListSerializer

        if self.action == "create":
            return RouteCreateSerializer

        if self.action == "retrieve":
            return RouteDetailSerializer


class AirplaneTypeViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    GenericViewSet
):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer

    def get_queryset(self):
        queryset = self.queryset

        name = self.request.query_params.get("name")
        if name:
            queryset = queryset.filter(name__icontains=name)

        return queryset


class AirplaneViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    GenericViewSet
):
    queryset = Airplane.objects.all()

    def get_queryset(self):
        queryset = self.queryset

        name = self.request.query_params.get("name")
        airplane_type = self.request.query_params.get("airplane_type")
        if name:
            queryset = queryset.filter(name__icontains=name)

        if airplane_type:
            queryset = queryset.filter(
                airplane_type__name__icontains=airplane_type
            )

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return AirplaneListSerializer

        if self.action == "create":
            return AirplaneCreateSerializer

        if self.action == "retrieve":
            return AirplaneDetailSerializer


class FlightViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    GenericViewSet
):
    queryset = Flight.objects.all()

    def get_queryset(self):
        queryset = self.queryset

        from_ = self.request.query_params.get("from")
        to = self.request.query_params.get("to")
        departure = self.request.query_params.get("departure_time")
        arrival = self.request.query_params.get("arrival_time")

        if from_:
            queryset = queryset.filter(
                route__source__closet_big_city__icontains=from_
            )

        if to:
            queryset = queryset.filter(
                route__destination__closet_big_city__icontains=to
            )

        if departure:
            departure_datetime = datetime.strptime(
                departure, "%Y-%m-%dT%H:%M:%SZ"
            )

            queryset = queryset.filter(
                departure_time=departure_datetime
            )

        if arrival:
            arrival_datetime = datetime.strptime(
                arrival, "%Y-%m-%dT%H:%M:%SZ"
            )

            queryset = queryset.filter(
                arrival_time=arrival_datetime
            )

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return FlightListSerializer

        if self.action == "create":
            return FLightCreateSerializer

        if self.action == "retrieve":
            return FLightDetailSerializer


class OrderViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    GenericViewSet
):
    queryset = Order.objects.all()
    serializer_class = OrderCreateSerializer

    def get_queryset(self):
        queryset = self.queryset.filter(
            user=self.request.user
        )

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer

        if self.action == "create":
            return OrderCreateSerializer

        if self.action == "retrieve":
            return OrderDetailSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
