from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from airport_service.models import (
    Crew,
    Airport,
    Route,
    AirplaneType,
    Airplane,
    Flight,
    Ticket,
    Order,
)


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name")


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = ("id", "name", "closet_big_city")


class RouteCreateSerializer(serializers.ModelSerializer):

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


class RouteListSerializer(RouteCreateSerializer):
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


class RouteDetailSerializer(RouteCreateSerializer):
    source = AirportSerializer(many=False, read_only=True)
    destination = AirportSerializer(many=False, read_only=True)


class AirplaneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneType
        fields = ("id", "name")


class AirplaneCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airplane
        fields = ("id", "name", "rows", "seats_in_rows", "airplane_type", "num_of_seats")


class AirplaneListSerializer(AirplaneCreateSerializer):
    airplane_type = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field="name"
    )


class AirplaneDetailSerializer(AirplaneCreateSerializer):
    airplane_type = AirplaneTypeSerializer(many=False, read_only=True)


class FLightCreateSerializer(serializers.ModelSerializer):

    def validate(self, attrs):
        data = super(FLightCreateSerializer, self).validate(attrs)
        Flight.validate_arrival(
            departure_time=attrs["departure_time"],
            arrival_time=attrs["arrival_time"],
            error_to_raise=ValidationError
        )
        return data

    class Meta:
        model = Flight
        fields = ("id", "route", "airplane", "departure_time", "arrival_time", "crew")


class FlightListSerializer(FLightCreateSerializer):
    route = RouteListSerializer(many=False, read_only=True)
    airplane = serializers.StringRelatedField(many=False, read_only=True)
    crew = serializers.StringRelatedField(many=True, read_only=True)


class FLightDetailSerializer(FLightCreateSerializer):
    route = RouteDetailSerializer(many=False, read_only=True)
    airplane = AirplaneDetailSerializer(many=False, read_only=True)
    crew = CrewSerializer(many=True, read_only=True)


class TicketCreateSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        data = super(TicketCreateSerializer, self).validate(attrs)
        Ticket.validate_seat_and_row(
            seat=attrs["seat"],
            row=attrs["row"],
            airplane_seats_in_row=attrs["flight"].airplane.seats_in_rows,
            airplane_rows=attrs["flight"].airplane.rows,
            error_to_raise=ValidationError
        )

        return data

    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "flight")


class TicketListSerializer(TicketCreateSerializer):
    source = serializers.CharField(
        source="flight.route.source"
    )
    destination = serializers.CharField(
        source="flight.route.destination"
    )

    class Meta(TicketCreateSerializer.Meta):
        fields = ("id", "row", "seat", "source", "destination")


class TicketDetailSerializer(TicketCreateSerializer):
    flight = FLightDetailSerializer(many=False, read_only=True)


class OrderCreateSerializer(serializers.ModelSerializer):
    tickets = TicketCreateSerializer(
        many=True,
        read_only=False,
        allow_empty=False
    )

    class Meta:
        model = Order
        fields = ("id", "tickets", "created_at")

    def create(self, validated_data):
        with transaction.atomic():
            ticket_data = validated_data.pop("tickets")
            order = Order.objects.create(**validated_data)
            for track_data in ticket_data:
                Ticket.objects.create(order=order, **track_data)
            return order


class OrderListSerializer(OrderCreateSerializer):
    tickets = TicketListSerializer(many=True, read_only=True)


class OrderDetailSerializer(OrderCreateSerializer):
    tickets = TicketDetailSerializer(many=True, read_only=True)
