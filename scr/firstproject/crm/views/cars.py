
from rest_framework import viewsets, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from django.db.models import Q

from ..serializers import CarSerializer
from ..models import Cars, Orders
from ..pagination import PaginationHandlerMixin, BasicPagination


class CarList(viewsets.ViewSet, PaginationHandlerMixin):
    permission_classes = [IsAuthenticated]
    authentication_classes = (TokenAuthentication,)
    pagination_class = BasicPagination

    def list(self, request):
        user_id = Token.objects.get(key=request.user.auth_token).user.id
        if request.user.is_rent:
            cars = Cars.objects.filter(rent_id__exact=user_id).order_by('-status')
        elif request.user.is_superuser:
            cars = Cars.objects.all().order_by('-status')
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)
        page = self.paginate_queryset(cars)
        if page is not None:
            serializer = self.get_paginated_response(CarSerializer(page, many=True).data)
        else:
            serializer = CarSerializer(cars, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request):
        try:
            request.data._mutable = True
        except AttributeError:
            pass
        request.data['rent_id'] = Token.objects.get(key=request.user.auth_token).user.id
        serializer = CarSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        user_id = Token.objects.get(key=request.user.auth_token).user.id
        car = get_object_or_404(Cars, pk=pk, rent_id=user_id)
        serializer = CarSerializer(car)
        return Response(serializer.data)

    def update(self, request, pk):
        user_id = Token.objects.get(key=request.user.auth_token).user.id
        car = Cars.objects.get(pk=pk, rent_id=user_id)
        serializer = CarSerializer(car, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk):
        user_id = Token.objects.get(key=request.user.auth_token).user.id
        car = Cars.objects.get(pk=pk, rent_id=user_id)
        if car.status in ['occupied', 'reserved']:
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        else:
            car.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


class CarFilter(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = (TokenAuthentication,)

    def get(self, request):
        start, end, brand, model, color = request.GET.get('start'), request.GET.get('end'), request.GET.get('brand'), \
                                          request.GET.get('model'), request.GET.get('color')
        only_color = request.GET.get('only_color')
        rent_id = Token.objects.get(key=request.user.auth_token).user.id
        if only_color:
            cars = Cars.objects.filter(
                rent_id=rent_id,
                color__icontains=only_color
            )
            return Response(CarSerializer(cars, many=True).data)
        if start and end:
            # start = datetime.strptime(start, '%d-%m-%Y').strftime('%Y-%m-%d')
            # end = datetime.strptime(end, '%d-%m-%Y').strftime('%Y-%m-%d')
            orders = Orders.objects.filter(
                Q(start__range=[start, end]) | Q(end__range=[start, end]) | Q(start__lt=start, end__gt=end),
                status__in=('in progress', 'reserved'), rent_id=rent_id).values_list('car_id', flat=True)

        elif start:
            # start = datetime.strptime(start, '%d-%m-%Y').strftime('%Y-%m-%d')
            orders = Orders.objects.filter(
                Q(start__lt=start),
                status__in=('in progress', 'reserved')
            ).values_list('car_id', flat=True),
        else:
            orders = Orders.objects.filter(rent_id=rent_id, status__in=('in progress', 'reserved'))

        if brand and model and color:
            cars = Cars.objects.filter(~Q(pk__in=orders), rent_id=rent_id, brand__icontains=brand,
                                       model__icontains=model, color__icontains=color)

        elif brand and color:
            cars = Cars.objects.filter(~Q(pk__in=orders), rent_id=rent_id, brand__icontains=brand,
                                       color__icontains=color)

        elif model and color:
            cars = Cars.objects.filter(~Q(pk__in=orders), rent_id=rent_id, model__icontains=model,
                                       color__icontains=color)

        elif brand:
            cars = Cars.objects.filter(~Q(pk__in=orders), rent_id=rent_id, brand__icontains=brand)

        elif model:
            cars = Cars.objects.filter(~Q(pk__in=orders), rent_id=rent_id, model__icontains=model)

        else:
            cars = Cars.objects.filter(~Q(pk__in=orders), rent_id=rent_id)
        serializer = CarSerializer(cars, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class BrandAndModelView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = (TokenAuthentication,)

    def get(self, request):
        rent_id = Token.objects.get(key=request.user.auth_token).user.id
        brands = list(set(Cars.objects.filter(rent_id=rent_id).values_list('brand', flat=True)))
        answer = []
        for i in brands:
            dict1 = {}
            models = list(set(Cars.objects.filter(rent_id=rent_id, brand=i).values_list('model', flat=True)))
            dict1[i] = models
            answer += [dict1]
        return Response(answer, status=status.HTTP_200_OK)
