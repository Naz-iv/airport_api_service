from django.db.models import F, Count, Q
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
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
    RouteListSerializer,
    TicketListSerializer,
    FlightListSerializer,
    OrderListSerializer,
    OrderDetailSerializer,
    AirplaneDetailSerializer,
    FlightDetailSerializer,
    TicketDetailSerializer,
    RouteDetailSerializer,
)


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer
    permission_classes = (AllowAny,)

    def get_queryset(self):
        """Get crew member by name or surname"""
        search_query = self.request.query_params.get("search")

        if search_query:
            return self.queryset.filter(
                Q(first_name__icontains=search_query)
                | Q(last_name__icontains=search_query))
        return self.queryset


class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer
    permission_classes = (AllowAny,)

    def get_queryset(self):
        """Get airport by name"""
        name = self.request.query_params.get("name")

        if name:
            return self.queryset.filter(name__icontains=name)

        return self.queryset


class OrderPagination(PageNumberPagination):
    page_size = 2
    page_size_query_param = "page_size"
    max_page_size = 100


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    permission_classes = (AllowAny,)
    pagination_class = OrderPagination

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer
        if self.action == "retrieve":
            return OrderDetailSerializer

        return OrderSerializer

    def get_queryset(self):
        return self.queryset.prefetch_related(
            "tickets",
            "tickets__flight",
            "tickets__flight__crew",
            "tickets__flight__airplane",
            "tickets__flight__route__source",
            "tickets__flight__route__destination",
        )


class AirplaneTypeViewSet(viewsets.ModelViewSet):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer
    permission_classes = (AllowAny,)


class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.all()
    permission_classes = (AllowAny,)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return AirplaneDetailSerializer

        return AirplaneSerializer


class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.all()
    permission_classes = (AllowAny,)

    def get_serializer_class(self):
        if self.action == "list":
            return FlightListSerializer
        if self.action == "retrieve":
            return FlightDetailSerializer
        return FlightSerializer

    def get_queryset(self):
        return self.queryset.prefetch_related(
            "airplane", "route__source", "route__destination", "crew"
        ).annotate(
            tickets_available=(
                F("airplane__rows") * F("airplane__seats") - Count("tickets")
            )
        )


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    permission_classes = (AllowAny,)

    def get_serializer_class(self):
        if self.action == "list":
            return TicketListSerializer
        if self.action == "retrieve":
            return TicketDetailSerializer
        return TicketSerializer

    def get_queryset(self):
        return self.queryset.prefetch_related(
            "flight",
            "order__user",
            "flight__route",
            "flight__route__source",
            "flight__route__destination",
            "flight__airplane",
        )


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all()
    permission_classes = (AllowAny,)

    def get_serializer_class(self):
        if self.action == "list":
            return RouteListSerializer
        if self.action == "retrieve":
            return RouteDetailSerializer

        return RouteSerializer

    def get_queryset(self):
        return self.queryset.select_related("source", "destination")
