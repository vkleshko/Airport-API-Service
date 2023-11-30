from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from airport_service.models import (
    Crew,
    Airport,
    Route,
    AirplaneType,
)
from airport_service.serializers import (
    CrewSerializer,
    AirportSerializer,
    RouteListSerializer,
    RouteCreateSerializer,
    RouteDetailSerializer,
    AirplaneTypeSerializer,
)


class CrewViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    GenericViewSet
):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer


class AirportViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    GenericViewSet
):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer


class RouteViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    GenericViewSet
):
    queryset = Route.objects.all()

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
