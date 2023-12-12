from datetime import datetime

from django.db.models import F, Count, Q
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAdminUser, IsAuthenticated

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
from flight_service.permissions import IsAdminOrAuthenticatedReadOnly
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


class CustomPagination(PageNumberPagination):
    page_size = 2
    page_size_query_param = "page_size"
    max_page_size = 100


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer
    permission_classes = (IsAdminUser,)

    def get_queryset(self):
        """Get crew member by name or surname"""
        search_query = self.request.query_params.get("search")

        if search_query:
            return self.queryset.filter(
                Q(first_name__icontains=search_query)
                | Q(last_name__icontains=search_query)
            )
        return self.queryset

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="search crew member",
                type={"type": "string", "items": {"type": "string"}},
                description="Search crew member by first_name or last_name (ex. ?search=Joe)"
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer
    permission_classes = (IsAdminOrAuthenticatedReadOnly,)

    def get_queryset(self):
        """Get airport by name"""
        name = self.request.query_params.get("name")

        if name:
            return self.queryset.filter(name__icontains=name)

        return self.queryset

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="name",
                type={"type": "string", "items": {"type": "string"}},
                description="Search airport by name (ex. ?name=Heathrow)"
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.prefetch_related(
        "tickets",
        "tickets__flight",
        "tickets__flight__crew",
        "tickets__flight__airplane",
        "tickets__flight__route__source",
        "tickets__flight__route__destination",
    )
    permission_classes = (IsAuthenticated,)
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer
        if self.action == "retrieve":
            return OrderDetailSerializer

        return OrderSerializer

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AirplaneTypeViewSet(viewsets.ModelViewSet):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer
    permission_classes = (IsAdminOrAuthenticatedReadOnly,)


class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.all()
    permission_classes = (IsAdminOrAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return AirplaneDetailSerializer

        return AirplaneSerializer

    def get_queryset(self):
        """Search airplane by type or name"""

        type_id = self.request.query_params.get("type")
        name = self.request.query_params.get("name")

        if type_id:
            self.queryset = self.queryset.select_related("airplane_type").filter(
                airplane_type__id=int(type_id)
            )

        if name:
            self.queryset = self.queryset.filter(name__icontains=name)

        return self.queryset

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="type",
                type={"type": "string", "items": {"type": "string"}},
                description="Search airplane by type id (ex. ?type=1)"
            ),
            OpenApiParameter(
                name="name",
                type={"type": "string", "items": {"type": "string"}},
                description="Search airplane by name (ex. ?name=Airbus)"
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.all()
    permission_classes = (IsAdminOrAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action == "list":
            return FlightListSerializer
        if self.action == "retrieve":
            return FlightDetailSerializer
        return FlightSerializer

    def get_queryset(self):
        """Search flight by departure date, source or destination"""

        date = self.request.query_params.get("date")
        source = self.request.query_params.get("source")
        destination = self.request.query_params.get("destination")

        self.queryset = self.queryset.prefetch_related(
            "airplane", "route__source", "route__destination", "crew"
        )

        if date:
            date = datetime.strptime(date, "%Y-%m-%d").date()
            self.queryset = self.queryset.filter(departure_time__date=date)

        if source:
            self.queryset = self.queryset.filter(route__source__name__icontains=source)

        if destination:
            self.queryset = self.queryset.filter(
                route__destination__name__icontains=destination
            )

        return self.queryset.annotate(
            tickets_available=(
                F("airplane__rows") * F("airplane__seats") - Count("tickets")
            )
        )

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="date",
                type={"type": "string", "items": {"type": "string"}},
                description="Search flight by departure date (ex. ?date=2023-12-27)"
            ),
            OpenApiParameter(
                name="source",
                type={"type": "string", "items": {"type": "string"}},
                description="Search flight by source airport name (ex. ?source=Heathrow)"
            ),
            OpenApiParameter(
                name="destination",
                type={"type": "string", "items": {"type": "string"}},
                description="Search flight by destination airport name (ex. ?destination=Kingsford)"
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class TicketViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ticket.objects.prefetch_related(
        "flight",
        "order__user",
        "flight__route",
        "flight__route__source",
        "flight__route__destination",
        "flight__airplane",
    )
    permission_classes = (IsAuthenticated,)
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.action == "list":
            return TicketListSerializer
        if self.action == "retrieve":
            return TicketDetailSerializer
        return TicketSerializer

    def get_queryset(self):
        return self.queryset.filter(order__user=self.request.user)


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all()
    permission_classes = (IsAdminOrAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action == "list":
            return RouteListSerializer
        if self.action == "retrieve":
            return RouteDetailSerializer

        return RouteSerializer

    def get_queryset(self):
        return self.queryset.select_related("source", "destination")
