from rest_framework import viewsets, generics, filters, status, parsers, permissions
from .models import RoomType, Room
from rooms import serializers, paginators
from rest_framework.decorators import action
from rest_framework.response import Response


class RoomTypeViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = RoomType.objects.all()
    serializer_class = serializers.RoomTypeSerializer


class RoomViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = Room.objects.filter(active=True)
    serializer_class = serializers.RoomSerializer
    pagination_class = paginators.ItemPaginator


    # Cách 1 để lọc
    # Tìm liếm theo q và roomtpye_id
    def get_queryset(self):
        query = self.request

        q = self.request.query_params.get('q')
        if q:
            query = query.filter(subject__icontains=q)

        roomtype_id = self.request.query_params.get('roomtype_id')
        if roomtype_id:
            query = query.filter(roomtype_id=roomtype_id)
        return query

    # Cách 2 để lọc
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ['room_number']
    ordering_fields = ['roomtype_id']