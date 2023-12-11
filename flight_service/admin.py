from django.contrib import admin

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


admin.site.register(Crew)
admin.site.register(Airport)
admin.site.register(Order)
admin.site.register(AirplaneType)
admin.site.register(Airplane)
admin.site.register(Flight)
admin.site.register(Ticket)
admin.site.register(Route)
