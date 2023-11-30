from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from airport_service.models import (
    Crew,
    Airport,
    Route,
    AirplaneType,
    Airplane,
)


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name")


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = ("id", "name", "closet_big_city")


class RouteListSerializer(serializers.ModelSerializer):
    source = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field="name"
    )
    destination = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field="name"
    )

    def validate(self, attrs):
        data = super(RouteListSerializer, self).validate(attrs)
        Route.validate_destination(
            source=attrs["source"],
            destination=attrs["destination"],
            error_to_raise=ValidationError
        )
        return data

    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")


class RouteCreateSerializer(RouteListSerializer):
    source = AirportSerializer(many=False, read_only=False)
    destination = AirportSerializer(many=False, read_only=False)


class RouteDetailSerializer(RouteListSerializer):
    source = AirportSerializer(many=False, read_only=True)
    destination = AirportSerializer(many=False, read_only=True)


class AirplaneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneType
        fields = ("id", "name")


class AirplaneListSerializer(serializers.ModelSerializer):
    airplane_type = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field="name"
    )

    class Meta:
        model = Airplane
        fields = ("id", "name", "rows", "seats_in_rows", "airplane_type", "num_of_seats")


class AirplaneCreateSerializer(AirplaneListSerializer):
    airplane_type = AirplaneTypeSerializer(many=False, read_only=False)


class AirplaneDetailSerializer(AirplaneListSerializer):
    airplane_type = AirplaneTypeSerializer(many=False, read_only=True)
