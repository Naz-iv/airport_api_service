from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models


class Crew(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    def __str__(self):
        return self.first_name + " " + self.last_name


class Airport(models.Model):
    name = models.CharField(max_length=255)
    closest_big_city = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="orders"
    )

    def __str__(self):
        return f"Order #{self.id} created by {self.user}"


class AirplaneType(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Airplane(models.Model):
    name = models.CharField(max_length=255)
    rows = models.IntegerField(validators=[MinValueValidator(1)])
    seats = models.IntegerField(validators=[MinValueValidator(1)])
    airplane_type = models.ForeignKey(
        AirplaneType, related_name="airplanes", on_delete=models.CASCADE
    )

    @property
    def capacity(self) -> int:
        return self.rows * self.seats

    def __str__(self):
        return self.name


class Flight(models.Model):
    route = models.ForeignKey("Route", related_name="flights", on_delete=models.CASCADE)
    airplane = models.ForeignKey(
        Airplane, related_name="flights", on_delete=models.CASCADE
    )
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    crew = models.ManyToManyField(Crew, related_name="flights")

    def __str__(self):
        return f"Flight #{self.id}: {self.route}. Airplane: {self.airplane}"


class Ticket(models.Model):
    row = models.IntegerField()
    seat = models.IntegerField()
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name="tickets")
    order = models.ForeignKey("Order", on_delete=models.CASCADE, related_name="tickets")

    class Meta:
        unique_together = ("flight", "row", "seat")
        ordering = ["row", "seat"]

    @staticmethod
    def validate_ticket(row, seat, airplane, error_to_raise):
        if not 1 <= row <= airplane.rows:
            raise error_to_raise(
                f"Row should be in range (1, {airplane.rows}), not {row}"
            )
        if not 1 <= seat <= airplane.seats:
            raise error_to_raise(
                f"Seat should be in range (1, {airplane.seats}), not {seat}"
            )

    def clean(self):
        Ticket.validate_ticket(
            self.row,
            self.seat,
            self.flight.airplane,
            ValidationError,
        )

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        self.full_clean()
        return super(Ticket, self).save(
            force_insert, force_update, using, update_fields
        )

    def __str__(self):
        return f"Ticker #{self.id}: seat #{self.seat}, row #{self.row}"


class Route(models.Model):
    source = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name="route_sources")
    destination = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name="route_destinations")
    distance = models.IntegerField(validators=[MinValueValidator(1)])

    def __str__(self):
        return f"from {self.source} to {self.destination}"
