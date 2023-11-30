from django.urls import path, include
from rest_framework import routers

from airport_service.views import (
    CrewViewSet,
    AirportViewSet,
    RouteViewSet,
    AirplaneTypeViewSet,
)

router = routers.DefaultRouter()
router.register("crews", CrewViewSet)
router.register("airports", AirportViewSet)
router.register("routers", RouteViewSet)
router.register("airplane_types", AirplaneTypeViewSet)

urlpatterns = [
    path("", include(router.urls)),
]

app_name = "airport_service"
