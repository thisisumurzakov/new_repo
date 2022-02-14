
from rest_framework import viewsets, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

from ..serializers import OrderSerializer, OrderInformationSerializer
from ..models import Cars, Clients, Orders, Rent, OrderInformation
from ..pagination import PaginationHandlerMixin, BasicPagination


class OrderList(viewsets.ViewSet, PaginationHandlerMixin):
    permission_classes = [IsAuthenticated]
    authentication_classes = (TokenAuthentication,)
    pagination_class = BasicPagination

    def list(self, request):
        user = Token.objects.get(key=request.user.auth_token).user
        order_status = request.GET.get('status')
        if user.is_rent:
            if order_status in ['in progress', 'finished', 'reserved']:
                orders = Orders.objects.filter(rent_id__exact=user.id, status=order_status).order_by('-order_id')
            else:
                orders = Orders.objects.filter(rent_id__exact=user.id).order_by('-order_id')
        elif request.user.is_superuser:
            orders = Orders.objects.all()
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)
        page = self.paginate_queryset(orders)
        if page is not None:
            serializer = self.get_paginated_response(OrderSerializer(page, many=True).data)
        else:
            serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request):
        try:
            request.data._mutable = True
        except AttributeError:
            pass
        user = Token.objects.get(key=request.user.auth_token).user
        rent = Rent.objects.get(rent_id=user.id)
        request.data['rent_id'] = user.id
        request.data['order_number'] = rent.order_number
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid() and user.is_rent:
            serializer.save()
            rent.order_number = rent.order_number + 1
            rent.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        user_id = Token.objects.get(key=request.user.auth_token).user.id
        order = get_object_or_404(Orders, pk=pk, rent_id=user_id)
        serializer = OrderSerializer(order)
        return Response(serializer.data)

    def update(self, request, pk):
        user_id = Token.objects.get(key=request.user.auth_token).user.id
        orders = Orders.objects.filter(rent_id=user_id)
        order = get_object_or_404(orders, pk=pk)
        serializer = OrderSerializer(order, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            car_status = request.data.get('status')
            if car_status.lower() == 'finished':
                car = get_object_or_404(Cars, pk=order.car_id.car_id)
                client = get_object_or_404(Clients, pk=order.client_id.client_id)
                car.status = 'vacant'
                client.status = 'vacant'
                car.save()
                client.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk):
        user_id = Token.objects.get(key=request.user.auth_token).user.id
        orders = Orders.objects.filter(rent_id=user_id)
        order = get_object_or_404(orders, pk=pk)
        if order.status in ['in progress', 'reserved']:
            car = get_object_or_404(Cars, car_id=order.car_id.car_id, rent_id=user_id)
            client = get_object_or_404(Clients, client_id=order.client_id.client_id)
            car.status = 'vacant'
            client.status = 'vacant'
            car.save()
            client.save()
        order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ExtendedOrder(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    authentication_classes = (TokenAuthentication,)

    def list(self, request):
        user = Token.objects.get(key=request.user.auth_token).user
        order_id = request.GET.get('order_id')
        if order_id:
            orders = OrderInformation.objects.filter(order_id=order_id)

            if orders:
                serializer = OrderInformationSerializer(orders, many=True)
                return Response(data=serializer.data, status=status.HTTP_200_OK)
            return Response({}, status=status.HTTP_404_NOT_FOUND)
        return Response({}, status=status.HTTP_404_NOT_FOUND)

    def create(self, request):
        try:
            request.data._mutable = True
        except AttributeError:
            pass
        user = Token.objects.get(key=request.user.auth_token).user
        serializer = OrderInformationSerializer(data=request.data)
        if serializer.is_valid() and user.is_rent:
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        user_id = Token.objects.get(key=request.user.auth_token).user.id
        order = get_object_or_404(OrderInformation, pk=pk)
        serializer = OrderInformationSerializer(order)
        return Response(serializer.data)
