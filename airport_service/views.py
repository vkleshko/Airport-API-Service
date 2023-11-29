from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from airport_service.models import Crew
from airport_service.serializers import CrewSerializer


class CrewViewSet(mixins.ListModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.CreateModelMixin,
                  GenericViewSet
                  ):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer
