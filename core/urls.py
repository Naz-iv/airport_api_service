from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/user/", include("user.urls", namespace="user")),
    path("api/flight_service/", include("flight_service.urls", namespace="flight_service")),
    path("__debug__/", include("debug_toolbar.urls")),
]
