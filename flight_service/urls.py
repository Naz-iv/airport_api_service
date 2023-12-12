from django.urls import include, path
from rest_framework import routers
from flight_service.views import (
    CrewViewSet,
    AirportViewSet,
    OrderViewSet,
    AirplaneTypeViewSet,
    AirplaneViewSet,
    FlightViewSet,
    TicketViewSet,
    RouteViewSet,
)


router = routers.DefaultRouter()
router.register("crews", CrewViewSet)
router.register("airports", AirportViewSet)
router.register("orders", OrderViewSet)
router.register("airplane-types", AirplaneTypeViewSet)
router.register("airplanes", AirplaneViewSet)
router.register("flights", FlightViewSet)
router.register("tickets", TicketViewSet)
router.register("routes", RouteViewSet)

urlpatterns = [path("", include(router.urls))]

app_name = "flight-service"
