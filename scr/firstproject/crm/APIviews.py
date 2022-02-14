import os
from pathlib import Path
from datetime import datetime, date
import logging

from rest_framework import viewsets, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAdminUser
from rest_framework.views import APIView
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from num2words import num2words
from rest_framework.decorators import api_view

from .serializers import CarSerializer, ClientSerializer, RentUserSerializer, RentSerializer
from .models import Cars, Clients, Orders, RentUsers, Rent, OrderInformation
from .documentation import DocumentPreparation
from .const import MONTH_DICT

BASE_DIR = Path(__file__).resolve().parent.parent

log_path = os.path.join(BASE_DIR, 'logs/app.log')
logging.basicConfig(
    filename=log_path,
    format="%(process)d - %(asctime)s - %(levelname)s : %(message)s",
    level=logging.INFO,
    filemode='a',
)


class RentList(viewsets.ViewSet):
    permission_classes = [IsAdminUser, IsAuthenticated]
    authentication_classes = (TokenAuthentication,)

    def list(self, request):
        rents = Rent.objects.all()
        serializer = RentSerializer(rents, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RentUserList(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    authentication_classes = (TokenAuthentication,)

    # def list(self, request):
    #     rent_users = RentUsers.objects.all()
    #     serializer = RentUserSerializer(rent_users, many=True)
    #     return Response(serializer.data)

    def create(self, request):
        user_id = Token.objects.get(key=request.user.auth_token).user.id
        client_id = request.data.get('client_id')
        if client_id:
            serializer = RentUserSerializer(data={'rent_id': user_id, 'client_id': client_id, 'moved_from': True})
            condition = RentUsers.objects.filter(rent_id=user_id, client_id=client_id)
            if serializer.is_valid() and not condition:
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({}, status=status.HTTP_404_NOT_FOUND)


class LoginView(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'username': user.username
        }, status=status.HTTP_201_CREATED)


class Logout(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = (TokenAuthentication,)

    def get(self, request, format=None):
        request.user.auth_token.delete()
        return Response({'response': 'token deleted'}, status=status.HTTP_200_OK)


class FileDownloadListAPIView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = (TokenAuthentication,)

    def date_time_formatting(self, some_date, some_time=None):

        if some_date and some_time:
            return f"«{some_date.day}» {MONTH_DICT[some_date.month].upper()} {some_date.year}г. " \
                   f"«{some_time.hour}» часов «{some_time.minute}» минут"
        else:
            return f"«{some_date.day}» {MONTH_DICT[some_date.month].upper()} {some_date.year}г. "

    def separate_thousands(self, number):
        return f'{int(number):,}'.replace(',', ' ')

    def get(self, request):
        query = request.GET.get('order_id')
        extended_order = request.GET.get('extended_order_id')
        rent_id = Token.objects.get(key=request.user.auth_token).user.id
        if query:
            order = get_object_or_404(Orders, pk=query, rent_id=rent_id)
            car = get_object_or_404(Cars, pk=order.car_id.car_id)
            car = dict(CarSerializer(car).data)
            client = get_object_or_404(Clients, pk=order.client_id.client_id)
            client = dict(ClientSerializer(client).data)
            car.update(client)
            car['order_time'] = (order.end - order.start).days
            car['start'] = self.date_time_formatting(order.start)
            car['end'] = self.date_time_formatting(order.end)
            car['fullname'] = "{} {} {}".format(client['lastname'], client['firstname'], client['second_name'])
            car['initials'] = "{} {}.{}.".format(client['lastname'], client['firstname'][0], client['second_name'][0])
            car['cost_word'] = num2words(car['cost'], lang='ru')
            car['rent_cost_word'] = num2words(car['rent_cost'], lang='ru')
            car['order_number'] = order.order_number
            car['start_with_time'] = self.date_time_formatting(order.start, order.start_time)
            car['end_with_time'] = self.date_time_formatting(order.end, order.end_time)
            car['cost'] = self.separate_thousands(car['cost'])
            car['rent_cost'] = self.separate_thousands(car['rent_cost'])
            input_path = os.path.join(BASE_DIR, 'media/documents/LASETTI.docx')
            media_path = "media/orders/{}-{}-{}-{}.docx".format(car["brand"], car["model"], order.order_id,
                                                                order.client_id.client_id)
            output_path = os.path.join(BASE_DIR, media_path)
            doc = DocumentPreparation(input_path, output_path, car)
            doc.generate_document()
            return Response({"document": media_path, "filename": media_path.replace("media/orders/", "")})

        elif extended_order:
            order = get_object_or_404(OrderInformation, pk=extended_order)
            car = get_object_or_404(Cars, pk=order.order_id.car_id.car_id)
            car = dict(CarSerializer(car).data)
            client_id = order.order_id.client_id.client_id
            client = get_object_or_404(Clients, pk=client_id)
            client = dict(ClientSerializer(client).data)
            car.update(client)
            car['order_time'] = (order.to_date - order.from_date).days
            car['start'] = self.date_time_formatting(order.from_date)
            car['end'] = self.date_time_formatting(order.to_date)
            car['fullname'] = "{} {} {}".format(client['lastname'], client['firstname'], client['second_name'])
            car['initials'] = "{} {}.{}.".format(client['lastname'], client['firstname'][0], client['second_name'][0])
            car['cost_word'] = num2words(car['cost'], lang='ru')
            car['rent_cost_word'] = num2words(car['rent_cost'], lang='ru')
            car['order_number'] = order.order_number
            car['start_with_time'] = self.date_time_formatting(order.from_date, order.from_time)
            car['end_with_time'] = self.date_time_formatting(order.to_date, order.to_time)
            car['cost'] = self.separate_thousands(car['cost'])
            car['rent_cost'] = self.separate_thousands(car['rent_cost'])
            input_path = os.path.join(BASE_DIR, 'media/documents/LASETTI.docx')
            media_path = "media/orders/{}-{}-{}-{}-{}.docx".format(car["brand"], car["model"], order.order_id.order_id,
                                                                   client_id, order.id)
            output_path = os.path.join(BASE_DIR, media_path)

            doc = DocumentPreparation(input_path, output_path, car)
            doc.generate_document()
            return Response({"document": media_path, "filename": media_path.replace("media/orders/", "")})
        return Response({}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def scheduledtask(request):
    orders = Orders.objects.filter(status='in progress')
    today = datetime.today()
    today = date(today.year, today.month, today.day)
    for order in orders:
        if order.end < today:
            order.status = 'finished'
            order.save()
            car = Cars.objects.get(car_id=order.car_id.car_id)
            car.status = 'vacant'
            car.save()
            client = Clients.objects.get(client_id=order.client_id.client_id)
            client.status = 'vacant'
            client.save()
    return Response({}, status=status.HTTP_200_OK)

