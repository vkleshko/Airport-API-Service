from django.urls import path, include
from rest_framework import routers

from airport_service.views import (
    CrewViewSet,
    AirportViewSet,
    RouteViewSet,
)

router = routers.DefaultRouter()
router.register("crews", CrewViewSet)
router.register("airports", AirportViewSet)
router.register("routers", RouteViewSet)

urlpatterns = [
    path("", include(router.urls)),
]

app_name = "airport_service"
