import json

from rest_framework import viewsets, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view
import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from ..serializers import ClientSerializer, RentUserSerializer, ClientsFromTgSerializer, CarSerializer
from ..models import Clients, Rent, ClientsFromTg, Cars


@api_view(['GET', 'POST'])
def viewforbot(request):
    url_token = request.GET.get('token')
    if url_token:
        if request.method == 'GET':
            rent_id = get_object_or_404(Rent, url_token=url_token)
            cars = Cars.objects.filter(rent_id=rent_id, status='vacant')
            serializer = CarSerializer(cars, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif request.method == 'POST':
            try:
                request.data._mutable = True
            except AttributeError:
                pass
            rent_id = get_object_or_404(Rent, url_token=url_token)
            request.data['rent_id'] = rent_id
            passport = request.data.get('passport_series')
            if passport and not (ClientsFromTg.objects.filter(passport_series=passport, rent_id=rent_id)):
                client = ClientsFromTgSerializer(data=request.data, many=False)
                if client.is_valid():
                    client.save()
                    return Response(client.data, status=status.HTTP_201_CREATED)
                return Response(client.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                text = "Passport series is invalid or client with this passport is registered before"
                return Response({"error": text}, status=status.HTTP_502_BAD_GATEWAY)
        else:
            return Response({}, status=status.HTTP_401_UNAUTHORIZED)


class ConfirmApplications(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    authentication_classes = (TokenAuthentication,)

    def list(self, request):
        rent_id = Token.objects.get(key=request.user.auth_token).user.id
        clients = ClientsFromTg.objects.filter(rent_id=rent_id)
        serializer = ClientsFromTgSerializer(clients, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        rent_id = Token.objects.get(key=request.user.auth_token).user.id
        client = get_object_or_404(ClientsFromTg, client_id=pk, rent_id=rent_id)
        serializer = ClientsFromTgSerializer(client, many=False)
        return Response(serializer.data)

    def destroy(self, request, pk):
        client = get_object_or_404(ClientsFromTg, client_id=pk)
        rent_id = Token.objects.get(key=request.user.auth_token).user.id
        rent = Rent.objects.get(rent_id=rent_id)
        answer = request.GET.get('answer')
        if client.get_rent_id() == rent_id:
            if answer == 'confirmed':
                clientfromtg = ClientsFromTgSerializer(client, many=False).data
                chat_id = clientfromtg.get('chat_id')
                photo = clientfromtg['photo']
                del clientfromtg['client_id'], clientfromtg['rent_id'], clientfromtg['chat_id'], clientfromtg['photo']
                serializer = ClientSerializer(data=clientfromtg, many=False)
                if serializer.is_valid():
                    serializer.save()
                    client_id = serializer.data['client_id']
                    client_image = Clients.objects.get(client_id=client_id)
                    client_image.get_image_from_url(photo)
                    client_image.save()
                    rent_user = RentUserSerializer(data={"rent_id": rent_id,
                                                         'client_id': serializer.data['client_id']})
                    if rent_user.is_valid():
                        rent_user.save()
                        client.delete()
                        # url = "https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}".format(
                        #     rent.bot_token, chat_id, "Поздравляем вы успешно зарегестрировались!"
                        # )
                        # r = requests.get(url=url)
                        markup = InlineKeyboardMarkup([[
                            InlineKeyboardButton(text="Посмотреть свободные машины", callback_data='get_cars')
                        ]])
                        data = {
                            "chat_id": client.chat_id,
                            "text": "Поздравляем вы успешно зарегестрировались!",
                            "reply_markup": json.dumps(markup.to_dict())
                        }
                        url = "https://api.telegram.org/bot{}/sendMessage".format(rent.bot_token)
                        r = requests.post(url=url, data=data)
                        text = "Successfully added to db and status code for telegram bot is {}".format(r.status_code)
                        return Response({"Response": text},
                                        status=status.HTTP_204_NO_CONTENT)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                feedback = request.data.get('Response')
                client.delete()
                if feedback:
                    text = "Ваши данные не прошли верификацию\n{}".format(feedback)
                else:
                    text = "Ваши данные не прошли верификацию попробуйте связатся с арендодателем"

                markup = InlineKeyboardMarkup([[
                    InlineKeyboardButton(text="Попробовать заново", callback_data='try_again')
                ]])
                data = {
                    "chat_id": client.chat_id,
                    "text": text,
                    "reply_markup": json.dumps(markup.to_dict())
                }
                # url = "https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}".format(
                #     rent.bot_token,
                #     client.chat_id,
                #     text
                # )
                # r = requests.get(url=url)
                url = "https://api.telegram.org/bot{}/sendMessage".format(rent.bot_token)
                r = requests.post(url=url, data=data)
                text = "Successfully deleted and status code for telegram bot is {}".format(r.status_code)
            return Response({"Response": text}, status=status.HTTP_204_NO_CONTENT)
        return Response({"error": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)