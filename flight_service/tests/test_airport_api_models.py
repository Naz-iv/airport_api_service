from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from rest_framework.test import APIClient

from flight_service.models import Airport, Order, Ticket
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


class ModelsTests(TestCase):
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

    def test_crew_str_method(self):
        self.assertEqual(
            str(self.crew), f"{self.crew.first_name} {self.crew.last_name}"
        )

    def test_airport_str_method(self):
        self.assertEqual(str(self.airport1), self.airport1.name)

    def test_airport_ordering(self):
        self.airport1.name = "A test name"
        self.airport2.name = "B test name"
        airports = list(Airport.objects.all())

        self.assertEqual(airports, [self.airport1, self.airport2])

    def test_order_str_method(self):
        self.assertEqual(str(self.order), f"Order #{self.order.id}")

    def test_orders_ordering(self):
        order = sample_order()
        orders = list(Order.objects.all())

        self.assertEqual(orders, [order, self.order])

    def test_airplane_type_str_method(self):
        self.assertEqual(str(self.airplane_type), self.airplane_type.name)

    def test_airplane_str_method(self):
        self.assertEqual(str(self.airplane), self.airplane.name)

    def test_airplane_capacity_method(self):
        self.assertEqual(
            self.airplane.capacity, self.airplane.rows * self.airplane.seats
        )

    def test_flight_str_method(self):
        self.assertEqual(str(self.flight), f"Flight #{self.flight.id}")

    def test_route_str_method(self):
        self.assertEqual(
            str(self.route),
            f"from {self.route.source.name} to {self.route.destination.name}",
        )

    def test_ticket_str_method(self):
        self.assertEqual(
            str(self.ticket),
            f"Ticker #{self.ticket.id}: row #{self.ticket.row}, "
            f"seat #{self.ticket.seat}",
        )

    def test_tickets_ordering(self):
        ticket1 = sample_ticket(row=2, seat=2)
        ticket2 = sample_ticket(row=1, seat=4)
        ticket3 = sample_ticket(row=12, seat=1)
        ticket4 = sample_ticket(row=13, seat=1)

        tickets = list(Ticket.objects.all())

        self.assertEqual(tickets, [self.ticket, ticket2, ticket1, ticket3, ticket4])

    def test_tickets_unique_flight_sear_row_validation(self):
        sample_ticket(row=2, seat=2, flight_id=1)
        with self.assertRaises(ValidationError):
            sample_ticket(row=2, seat=2, flight_id=1)

    def test_tickets_seat_row_validation(self):
        self.airplane.rows = 100
        self.airplane.seats = 10

        with self.assertRaises(ValidationError):
            sample_ticket(row=0, seat=3, flight_id=1)

        with self.assertRaises(ValidationError):
            sample_ticket(row=3, seat=0, flight_id=1)

        with self.assertRaises(ValidationError):
            sample_ticket(row=101, seat=5, flight_id=1)

        with self.assertRaises(ValidationError):
            sample_ticket(row=4, seat=13, flight_id=1)
