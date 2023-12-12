from datetime import timedelta

from django.utils import timezone


from flight_service.models import (
    Crew,
    Airport,
    Order,
    AirplaneType,
    Route,
    Flight,
    Ticket,
    Airplane,
)


def sample_crew(**params):
    defaults = {
        "first_name": "Sample name",
        "last_name": "Sample surname",
    }
    defaults.update(params)
    return Crew.objects.create(**defaults)


def sample_airport(**params):
    defaults = {
        "name": "Sample name",
        "closest_big_city": "Sample City",
    }
    defaults.update(params)
    return Airport.objects.create(**defaults)


def sample_ticket(**params):
    defaults = {
        "row": Ticket.objects.count() + 1,
        "seat": Ticket.objects.count() + 1,
        "flight_id": 1,
        "order_id": 1,
    }
    defaults.update(params)
    return Ticket.objects.create(**defaults)


def sample_order(**params):
    defaults = {
        "created_at": timezone.now(),
        "user_id": 1,
    }
    defaults.update(params)
    return Order.objects.create(**defaults)


def sample_airplane_type(**params):
    defaults = {
        "name": "Sample name",
    }
    defaults.update(params)
    return AirplaneType.objects.create(**defaults)


def sample_airplane(**params):
    defaults = {"name": "Sample name", "rows": 20, "seats": 6, "airplane_type_id": 1}
    defaults.update(params)
    return Airplane.objects.create(**defaults)


def sample_route(**params):
    defaults = {"source_id": 1, "destination_id": 2, "distance": 100}
    defaults.update(params)
    return Route.objects.create(**defaults)


def sample_flight(**params):
    defaults = {
        "route_id": 1,
        "airplane_id": 1,
        "departure_time": timezone.now(),
        "arrival_time": timezone.now() + timedelta(hours=3),
    }
    defaults.update(params)
    return Flight.objects.create(**defaults)
