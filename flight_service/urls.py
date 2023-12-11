from django.urls import include, path
from rest_framework import routers
from flight_service.serializers import (
    CrewViewSet,
    AirportViewSet,
    OrderViewSet,
    AirplaneTypeViewSet,
    AirplaneViewSet,
    FlightsViewSet,
    TicketViewSet,
    RouteViewSet,
)


router = routers.DefaultRouter()
router.register("crews", CrewViewSet)
router.register("airports", AirportViewSet)
router.register("orders", OrderViewSet)
router.register("airplane_types", AirplaneTypeViewSet)
router.register("airplanes", AirplaneViewSet)
router.register("flights", FlightsViewSet)
router.register("ticket", TicketViewSet)
router.register("routes", RouteViewSet)

urlpatterns = [
    path("", include(router.urls))
]

app_name = "flight_service"
