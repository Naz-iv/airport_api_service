from rest_framework import viewsets
from rest_framework.permissions import AllowAny

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
from flight_service.serializers import (
    CrewSerializer,
    AirportSerializer,
    OrderSerializer,
    AirplaneTypeSerializer,
    AirplaneSerializer,
    FlightSerializer,
    TicketSerializer,
    RouteSerializer,
)


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer
    permission_classes = (AllowAny,)


class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer
    permission_classes = (AllowAny,)


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = (AllowAny,)


class AirplaneTypeViewSet(viewsets.ModelViewSet):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer
    permission_classes = (AllowAny,)


class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.all()
    serializer_class = AirplaneSerializer
    permission_classes = (AllowAny,)


class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer
    permission_classes = (AllowAny,)


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = (AllowAny,)


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer
    permission_classes = (AllowAny,)
