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


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order


class AirplaneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneType


class AirplaneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airplane


class FlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight


class TicketSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        data = super(TicketSerializer, self).validate(attrs=attrs)
        Ticket.validate_ticket(
            attrs["row"], attrs["seat"], attrs["flight"].airplane, ValidationError
        )
        return data

    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "flight")


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
