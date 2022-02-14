
from rest_framework import viewsets, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from django.db.models import Q


from ..serializers import BlackListSerializer
from ..models import Clients, BlackList


class ClientInfoFromBlackList(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    authentication_classes = (TokenAuthentication,)

    def list(self, request):
        query = request.GET.get('search')
        if query:
            client = Clients.objects.get(
                Q(passport_series__icontains=query)
            )
            rent_id = Token.objects.get(key=request.user.auth_token).user.id
            clients = BlackList.objects.filter(rent_id=rent_id, client_id=client)
            serializer = BlackListSerializer(clients, many=True)
            return Response(serializer.data)
        return Response({}, status=status.HTTP_404_NOT_FOUND)

    def create(self, request):
        try:
            request.data._mutable = True
        except AttributeError:
            pass
        request.data['rent_id'] = Token.objects.get(key=request.user.auth_token).user.id
        serializer = BlackListSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        client = get_object_or_404(BlackList, client_id=pk)
        serializer = BlackListSerializer(client)
        return Response(serializer.data)

    def update(self, request, pk):
        client = get_object_or_404(BlackList, pk=pk)
        serializer = BlackListSerializer(client, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk):
        client = get_object_or_404(BlackList, client_id=pk)
        user_id = Token.objects.get(key=request.user.auth_token).user.id
        if client.get_rent_id() == user_id:
            client.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
