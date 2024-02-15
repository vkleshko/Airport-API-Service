from django.urls import path, include
from rest_framework import routers

from airport_service.views import (
    CrewViewSet,
    AirportViewSet,
    RouteViewSet,
    AirplaneTypeViewSet,
    AirplaneViewSet,
    OrderViewSet,
    flight_list,
    flight_detail,
)

router = routers.DefaultRouter()
router.register("crews", CrewViewSet)
router.register("airports", AirportViewSet)
router.register("routers", RouteViewSet)
router.register("airplane_types", AirplaneTypeViewSet)
router.register("airplanes", AirplaneViewSet)
router.register("orders", OrderViewSet)

urlpatterns = [
    path("flights/", flight_list, name="flight-list"),
    path("flights/<int:pk>/", flight_detail, name="flight-detail"),
    path("", include(router.urls)),
]

app_name = "airport_service"
