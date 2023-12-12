from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from flight_service.models import (
    Crew,
    Airport,
    Order,
    AirplaneType,
    Airplane,
    Flight,
    Ticket,
    Route,
)


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = "__all__"


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = "__all__"


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = "__all__"


class RouteListSerializer(RouteSerializer):
    source = serializers.SlugField(source="source.name", read_only=True)
    destination = serializers.SlugField(source="destination.name", read_only=True)

    class Meta:
        model = Route
        fields = ("id", "source", "destination")


class RouteDetailSerializer(RouteSerializer):
    source = AirportSerializer(read_only=False, many=False)
    destination = AirportSerializer(read_only=False, many=False)


class FlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = "__all__"


class FlightListSerializer(FlightSerializer):
    route = RouteListSerializer(read_only=True, many=False)
    airplane = serializers.StringRelatedField(read_only=True, many=False)
    crew = serializers.StringRelatedField(read_only=True, many=True)
    tickets_available = serializers.IntegerField(read_only=True)

    class Meta:
        model = Flight
        fields = (
            "id",
            "route",
            "airplane",
            "crew",
            "tickets_available",
            "departure_time",
            "arrival_time",
        )


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = "__all__"

    def validate(self, attrs):
        data = super(TicketSerializer, self).validate(attrs=attrs)
        Ticket.validate_ticket(
            attrs["row"], attrs["seat"], attrs["flight"].airplane, ValidationError
        )
        return data


class TicketFlightDetailSerializer(FlightListSerializer):
    route = RouteListSerializer(read_only=True, many=False)

    class Meta:
        model = Flight
        fields = ("route", "airplane", "departure_time", "arrival_time")


class TicketListSerializer(TicketSerializer):
    flight = TicketFlightDetailSerializer(many=False, read_only=True)


class TicketDetailSerializer(TicketListSerializer):
    flight = TicketFlightDetailSerializer(many=False, read_only=True)

    class Meta:
        model = Ticket
        fields = (
            "id",
            "flight",
            "row",
            "seat",
        )


class TicketSeatSerializer(TicketDetailSerializer):
    class Meta:
        model = Ticket
        fields = ("row", "seat")


class AirplaneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airplane
        fields = "__all__"


class AirplaneDetailSerializer(AirplaneSerializer):
    airplane_type = serializers.SlugField(source="airplane_type.name")

    class Meta:
        model = Airplane
        fields = ("id", "name", "rows", "seats", "capacity", "airplane_type")


class FlightDetailSerializer(FlightSerializer):
    route = RouteDetailSerializer(many=False, read_only=True)
    airplane = AirplaneDetailSerializer(many=False, read_only=True)

    seats_taken = TicketSeatSerializer(source="tickets", many=True, read_only=True)

    class Meta:
        model = Flight
        fields = (
            "id",
            "route",
            "airplane",
            "crew",
            "departure_time",
            "arrival_time",
            "seats_taken",
        )


class OrderTicketSerializer(TicketSerializer):
    class Meta:
        model = Ticket
        fields = ("flight", "row", "seat")


class OrderSerializer(serializers.ModelSerializer):
    tickets = OrderTicketSerializer(many=True, read_only=False, allow_empty=False)

    class Meta:
        model = Order
        fields = "__all__"

    def create(self, validated_data):
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets")
            order = Order.objects.create(**validated_data)
            for ticket_data in tickets_data:
                Ticket.objects.create(order=order, **ticket_data)
            return order


class OrderListSerializer(OrderSerializer):
    tickets = TicketListSerializer(many=True, read_only=True)


class OrderDetailSerializer(OrderSerializer):
    tickets = TicketDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = "__all__"


class AirplaneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneType
        fields = "__all__"
