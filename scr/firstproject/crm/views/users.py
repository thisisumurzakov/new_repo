
from rest_framework import viewsets, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth.hashers import make_password
from rest_framework.permissions import IsAdminUser
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

from ..serializers import UserSerializer
from ..models import User, Rent, SuperUser
from ..pagination import PaginationHandlerMixin, BasicPagination


class UserList(viewsets.ViewSet, PaginationHandlerMixin):
    permission_classes = [IsAuthenticated, IsAdminUser]
    authentication_classes = (TokenAuthentication,)
    pagination_class = BasicPagination

    def list(self, request):
        users = User.objects.all()
        page = self.paginate_queryset(users)
        if page is not None:
            serializer = self.get_paginated_response(UserSerializer(page, many=True).data)
        else:
            serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create_data(self, user):
        return {'response': 'all present and correct!', 'username': user.username,
                'token': Token.objects.get(user=user).key}

    def create(self, request):
        try:
            request.data._mutable = True
        except AttributeError:
            pass
        if request.data['is_rent']:
            # request.data['date_of_birth'] = datetime.strptime(request.data['date_of_birth'],
            #                                                   '%d-%m-%Y').strftime('%Y-%m-%d')
            # request.data['date_of_issue'] = datetime.strptime(request.data['date_of_issue'],
            #                                                   '%d-%m-%Y').strftime('%Y-%m-%d')
            rent_name = request.data['rent_name']
            rent_phone_no = request.data['rent_phone_no']
            document_num = request.data['document_num']
            del request.data['rent_name'], request.data['rent_phone_no'], request.data['document_num']
            request.data['password'] = make_password(request.data['password'])
            serializer = UserSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()
                Rent.objects.create(rent_id=user, rent_name=rent_name, rent_phone_no=rent_phone_no,
                                    document_num=document_num)
                data = self.create_data(user)
                return Response(data, status=status.HTTP_201_CREATED)
        elif request.data['is_superuser']:
            try:
                del request.data['rent_name'], request.data['rent_phone_no'], request.data['document_num']
            except TypeError:
                print('ERROR')
            serializer = UserSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()
                SuperUser.objects.create(user=user)
                data = self.create_data(user)
                return Response(data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def retrieve(self, request, pk=None):
        users = User.objects.all()
        user = get_object_or_404(users, pk=pk)
        serializer = UserSerializer(user)
        return Response(serializer.data)

    def update(self, request, pk):
        user = User.objects.get(pk=pk)
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            user = serializer.save()
            return Response(self.create_data(user=user))
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk):
        user = User.objects.get(pk=pk)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
