from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db.models import F, Count
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from flight_service.models import Crew, Airport, Order, Route, Flight, Ticket
from flight_service.serializers import (
    AirportSerializer,
    FlightListSerializer,
    OrderListSerializer,
    FlightDetailSerializer,
    OrderDetailSerializer,
    RouteListSerializer,
    TicketListSerializer,
    RouteDetailSerializer,
    TicketDetailSerializer,
    CrewSerializer,
)
from flight_service.tests.sample_functions import (
    sample_crew,
    sample_airplane_type,
    sample_airplane,
    sample_airport,
    sample_route,
    sample_order,
    sample_flight,
    sample_ticket,
)


FLIGHT_URL = reverse("flight-service:flight-list")
CREW_URL = reverse("flight-service:crew-list")
AIRPORT_URL = reverse("flight-service:airport-list")
ORDER_URL = reverse("flight-service:order-list")
AIRPLANE_TYPE_URL = reverse("flight-service:airplanetype-list")
AIRPLANE_URL = reverse("flight-service:airplane-list")
TICKET_URL = reverse("flight-service:ticket-list")
ROUTE_URL = reverse("flight-service:route-list")


class UnauthenticatedApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_flight_auth_required(self):
        resp = self.client.get(FLIGHT_URL)

        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_crew_auth_required(self):
        resp = self.client.get(CREW_URL)

        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_airport_auth_required(self):
        resp = self.client.get(AIRPORT_URL)

        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_order_auth_required(self):
        resp = self.client.get(ORDER_URL)

        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_airplanetype_auth_required(self):
        resp = self.client.get(AIRPLANE_TYPE_URL)

        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_airplane_auth_required(self):
        resp = self.client.get(AIRPLANE_URL)

        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_ticket_auth_required(self):
        resp = self.client.get(TICKET_URL)

        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_route_auth_required(self):
        resp = self.client.get(ROUTE_URL)

        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create(
            email="admin@myproject.com", password="password"
        )
        self.client.force_authenticate(self.user)
        self.crew = sample_crew()
        self.airplane_type = sample_airplane_type()
        self.airplane = sample_airplane()
        self.airport1 = sample_airport()
        self.airport2 = sample_airport()
        self.route = sample_route()
        self.order = sample_order(user_id=self.user.id)
        self.flight = sample_flight()
        self.flight.crew.add(self.crew)
        self.ticket = sample_ticket()

    def test_list_flights(self):
        sample_flight()

        flights = Flight.objects.annotate(
            tickets_available=(
                F("airplane__rows") * F("airplane__seats") - Count("tickets")
            )
        )
        serializer = FlightListSerializer(flights, many=True)

        resp = self.client.get(FLIGHT_URL)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["results"], serializer.data)

    def test_retrieve_flight(self):
        sample_flight()

        flight = Flight.objects.filter(id=self.flight.id).first()
        serializer = FlightDetailSerializer(flight, many=False)

        resp = self.client.get(
            reverse("flight-service:flight-detail", args=[self.flight.id])
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data, serializer.data)

    def test_list_flights_filter_by_date(self):
        flight = sample_flight(departure_time=timezone.now() - timedelta(days=100))

        serializer = FlightListSerializer(
            Flight.objects.filter(id=flight.id)
            .annotate(
                tickets_available=(
                    F("airplane__rows") * F("airplane__seats") - Count("tickets")
                )
            )
            .first()
        )

        resp = self.client.get(
            FLIGHT_URL, {"data": f"{(timezone.now() - timedelta(days=100)).date()}"}
        )
        self.assertIn(serializer.data, resp.data["results"])

    def test_list_flights_filter_by_source(self):
        airport = sample_airport(name="Correct source")
        route = sample_route(source_id=airport.id)
        flight = sample_flight(
            departure_time=timezone.now() - timedelta(days=100), route_id=route.id
        )

        serializer = FlightListSerializer(
            Flight.objects.filter(id=flight.id)
            .annotate(
                tickets_available=(
                    F("airplane__rows") * F("airplane__seats") - Count("tickets")
                )
            )
            .first()
        )

        resp = self.client.get(FLIGHT_URL, {"source": "Correct"})
        self.assertIn(serializer.data, resp.data["results"])

    def test_list_flights_filter_by_destination(self):
        airport = sample_airport(name="Correct destination")
        route = sample_route(destination_id=airport.id)
        flight = sample_flight(
            departure_time=timezone.now() - timedelta(days=100), route_id=route.id
        )

        serializer = FlightListSerializer(
            Flight.objects.filter(id=flight.id)
            .annotate(
                tickets_available=(
                    F("airplane__rows") * F("airplane__seats") - Count("tickets")
                )
            )
            .first()
        )

        resp = self.client.get(FLIGHT_URL, {"destination": "Correct"})
        self.assertIn(serializer.data, resp.data["results"])

    def test_flight_admin_required(self):
        payload = {
            "route": self.route.id,
            "airplane": self.airplane.id,
            "departure_time": timezone.now(),
            "arrival_time": timezone.now() + timedelta(hours=3),
            "crew": [1],
        }

        resp = self.client.post(FLIGHT_URL, payload)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_crew_admin_required(self):
        payload = {
            "first_name": "Test name",
            "last_name": "Test surname",
        }

        resp = self.client.post(CREW_URL, payload)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_airports_list(self):
        sample_airport()
        airports = Airport.objects.all()
        serializer = AirportSerializer(airports, many=True)

        resp = self.client.get(AIRPORT_URL)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        self.assertEqual(resp.data["results"], serializer.data)

    def test_airports_filter_by_name(self):
        airport = sample_airport(name="Correct name")

        serializer = AirportSerializer(Airport.objects.get(id=airport.id))

        resp = self.client.get(AIRPORT_URL, {"name": "Correct"})

        self.assertIn(serializer.data, resp.data["results"])

    def test_airport_admin_required(self):
        payload = {
            "name": "Test name",
            "closest_big_city": "Test city",
        }

        resp = self.client.post(AIRPORT_URL, payload)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_orders_list(self):
        sample_order()
        orders = Order.objects.all()
        serializer = OrderListSerializer(orders, many=True)

        resp = self.client.get(ORDER_URL)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["results"], serializer.data)

    def test_retrieve_order(self):
        order = Order.objects.filter(id=self.order.id).first()
        serializer = OrderDetailSerializer(order, many=False)

        resp = self.client.get(
            reverse("flight-service:order-detail", args=[self.order.id])
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data, serializer.data)

    def test_rote_list(self):
        sample_route()
        routes = Route.objects.all()
        serializer = RouteListSerializer(routes, many=True)

        resp = self.client.get(ROUTE_URL)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        self.assertEqual(resp.data["results"], serializer.data)

    def test_retrieve_route(self):
        sample_route()

        route = Route.objects.filter(id=self.route.id).first()
        serializer = RouteDetailSerializer(route)

        resp = self.client.get(
            reverse("flight-service:route-detail", args=[self.route.id])
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data, serializer.data)

    def test_route_admin_required(self):
        payload = {}

        resp = self.client.post(ROUTE_URL, payload)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_ticket_list(self):
        sample_ticket()
        tickets = Ticket.objects.all()
        serializer = TicketListSerializer(tickets, many=True)

        resp = self.client.get(TICKET_URL)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        self.assertEqual(resp.data["results"], serializer.data)

    def test_retrieve_ticket(self):
        sample_ticket()

        ticket = Ticket.objects.filter(id=self.ticket.id).first()
        serializer = TicketDetailSerializer(ticket, many=False)

        resp = self.client.get(
            reverse("flight-service:ticket-detail", args=[self.flight.id])
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data, serializer.data)

    def test_ticket_viewset_read_only(self):
        payload = {}

        resp = self.client.post(TICKET_URL, payload)
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class AdminApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            email="admin@myproject.com", password="password"
        )
        self.client.force_authenticate(self.user)
        self.crew = sample_crew()
        self.airplane_type = sample_airplane_type()
        self.airplane = sample_airplane()
        self.airport1 = sample_airport()
        self.airport2 = sample_airport()
        self.route = sample_route()
        self.order = sample_order(user_id=self.user.id)
        self.flight = sample_flight()
        self.flight.crew.add(self.crew)
        self.ticket = sample_ticket()

    def test_list_crew(self):
        sample_crew()

        crews = Crew.objects.all()
        serializer = CrewSerializer(crews, many=True)

        resp = self.client.get(CREW_URL)

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["results"], serializer.data)

    def test_crew_creat_instance(self):
        payload = {"first_name": "Test", "last_name": "Test"}

        resp = self.client.post(CREW_URL, payload)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_airport_creat_instance(self):
        payload = {"name": "Test", "closest_big_city": "Test"}

        resp = self.client.post(AIRPORT_URL, payload)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_airplane_type_creat_instance(self):
        payload = {"name": "Test"}

        resp = self.client.post(AIRPLANE_TYPE_URL, payload)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_airplane_creat_instance(self):
        payload = {
            "name": "Test",
            "rows": 12,
            "seats": 3,
            "airplane_type": self.airplane_type.id,
        }

        resp = self.client.post(AIRPLANE_URL, payload)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_flight_creat_instance(self):
        payload = {
            "route": self.route.id,
            "airplane": self.airplane.id,
            "departure_time": timezone.now(),
            "arrival_time": timezone.now() + timedelta(hours=3),
            "crew": [self.crew.id],
        }

        resp = self.client.post(FLIGHT_URL, payload)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_route_creat_instance(self):
        payload = {
            "source": self.airport1.id,
            "destination": self.airport2.id,
            "distance": 100,
        }

        resp = self.client.post(ROUTE_URL, payload)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_retrieve_flight(self):
        sample_flight()

        flight = Flight.objects.filter(id=self.flight.id).first()
        serializer = FlightDetailSerializer(flight, many=False)

        resp = self.client.get(
            reverse("flight-service:flight-detail", args=[self.flight.id])
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data, serializer.data)
