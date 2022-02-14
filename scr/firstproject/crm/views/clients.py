
from rest_framework import viewsets, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from django.db.models import Q

from ..serializers import ClientSerializer, RentUserSerializer
from ..models import Clients, RentUsers
from ..pagination import PaginationHandlerMixin, BasicPagination


class ClientsList(viewsets.ViewSet, PaginationHandlerMixin):
    permission_classes = [IsAuthenticated]
    authentication_classes = (TokenAuthentication,)
    pagination_class = BasicPagination

    def get_client(self, request):
        user_id = Token.objects.get(key=request.user.auth_token).user.id
        users = RentUsers.objects.filter(rent_id__exact=user_id).values('client_id', )
        return Clients.objects.filter(pk__in=users)

    def list(self, request):
        query = request.GET.get('search')
        global_query = request.GET.get('global_search')
        if global_query:
            client = Clients.objects.filter(
                Q(passport_series__icontains=global_query)  # |
                # Q(firstname__icontains=global_query) |
                # Q(lastname__icontains=global_query)
            )
            serializer = ClientSerializer(client, many=True)
            return Response(serializer.data)
        elif query:
            clients = self.get_client(request)
            client = clients.filter(
                Q(passport_series__icontains=query) |
                Q(firstname__icontains=query) |
                Q(lastname__icontains=query)
            )
            serializer = ClientSerializer(client, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        elif request.user.is_rent:
            # clients = Clients.objects.raw("SELECT * FROM crm_clients")
            # cursor = connection.cursor()
            # cursor.execute("select * from crm_clients,(select * from crm_rentusers) as rent
            # where crm_clients.client_id = rent.client_id and rent.rent_id = 2")
            # clients = cursor.fetchall()
            # rent = RentUsers.objects.all()
            # clients = Clients.objects.raw("select * from crm_clients,(select client_id, rent_id from crm_rentusers)\
            #      where crm_clients.client_id = crm_rentusers.client_id and crm_rentusers.rent_id = 2")
            # clients = Clients.objects.raw("""
            # SELECT * FROM crm_clients
            # """)
            #
            # rents = RentUsers.objects.raw("""
            # SELECT * FROM crm_rentusers
            # """)

            # clients = Clients.objects.raw("""
            # select * from crm_clients inner join crm_rentusers on
            # crm_clients.client_id = crm_rentusers.client_id
            # where crm_rentusers.rent_id = 2
            # """)

            # result =
            # clients = Clients.objects.raw("""
            # select * from crm_clients where exists(select * from crm_rentusers where
            # crm_clients.client_id = crm_rentusers.client_id and crm_rentusers.rent_id = '{}'
            # )""".format(request.user.id))

            # clients = RentUsers.objects.select_related('rent').get()

            # clients = Clients.objects.extra(
            # select={'val': f"""SELECT Clients.* FROM Clients WHERE Clients.client_id = Rent_Users.client_id AND
            # Rent_Users.rent_id = '{request.user.id}'"""})
            # clients = Clients.objects.all()
            # clients = Clients.objects.filter(rent_id__fk=request.user.id)
            # user_id = Token.objects.get(key=request.user.auth_token).user.id
            # users = RentUsers.objects.filter(rent_id__exact=user_id).values('client_id',)
            # clients = Clients.objects.filter(pk__in=users)
            clients = self.get_client(request).order_by('-status', 'in_black_list')

        elif request.user.is_superuser:
            clients = Clients.objects.all().order_by('-status', 'in_black_list')

        else:
            return Response(status=status.HTTP_404_NOT_FOUND)
        page = self.paginate_queryset(clients)
        if page is not None:
            serializer = self.get_paginated_response(ClientSerializer(page, many=True).data)
        else:
            serializer = ClientSerializer(clients, many=True)
        # result = sorted(serializer.data, key=lambda k: k['status'], reverse=True)
        # result1 = sorted(result, key=lambda k: k['in_black_list'])
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request):
        try:
            request.data._mutable = True
        except AttributeError:
            pass
        user = Token.objects.get(key=request.user.auth_token).user
        request.data['rent_id'] = user.id
        serializer = ClientSerializer(data=request.data)
        if serializer.is_valid() and user.is_rent:
            serializer.save()
            rent_user = RentUserSerializer(data={"rent_id": user.id, 'client_id': serializer.data['client_id']})
            if rent_user.is_valid():
                rent_user.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        clients = self.get_client(request)
        client = get_object_or_404(clients, pk=pk)
        serializer = ClientSerializer(client)
        return Response(serializer.data)

    def update(self, request, pk):
        clients = self.get_client(request)
        client = get_object_or_404(clients, pk=pk)
        serializer = ClientSerializer(client, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk):
        client = get_object_or_404(Clients, pk=pk)
        if client.status in ['occupied', 'reserved']:
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        else:
            client.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
