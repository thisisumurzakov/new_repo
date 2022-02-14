from datetime import datetime, timedelta

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from django.db.models import Q

from ..serializers import CarCashflowserializer, TopClientsSerializer
from ..models import Cars, Orders, RentUsers


class Analytics(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = (TokenAuthentication,)

    def get_order_helper(self, rent_id, start, end):
        delta = end - start
        orders = Orders.objects.filter(Q(start__range=[start, end]) | Q(end__range=[start, end]), rent_id=rent_id)
        temp = []
        for i in range(delta.days + 1):
            day = (start + timedelta(days=i)).date()
            str_day = str(day)
            temp1 = {'orders_list': [], 'order_count': 0, 'profit': 0}
            for order in orders:
                # order_start = date(order.start.year, order.start.month, order.start.day)
                # order_end = date(order.end.year, order.end.month, order.end.day)
                if order.start <= day <= order.end:
                    temp1['orders_list'].append(order.order_id)
                    temp1['profit'] += float(order.car_id.rent_cost)
            temp1['order_count'] = len(temp1['orders_list'])
            temp.append({str_day: temp1})
        return Response(temp, status=status.HTTP_200_OK)

    def get_orders(self, request):
        rent_id = Token.objects.get(key=request.user.auth_token).user.id
        start = request.GET.get('start')
        end = request.GET.get('end')
        days = request.GET.get('days')
        if start and end:
            # orders1 = Orders.objects.filter(Q(start__range=[start, end]), Q(end__range=[start, end]), rent_id=rent_id)
            # orders2 = Orders.objects.filter(Q(start__range=[start, end], end__gt=end), rent_id=rent_id)
            # orders3 = Orders.objects.filter(Q(end__range=[start, end], start__lt=start), rent_id=rent_id)
            # count = Orders.objects.filter(Q(start__range=[start, end]), rent_id=rent_id).count()
            # order4 = Orders.objects.filter(rent_id=rent_id, start__range=[start, end]).extra(
            #     {'start': 'timestamp'}
            # ).values('order_id').annotate(orders_count=Count('order_id'))
            # print(order4)
            # return Response({'orders1': OrderSerializer(orders1, many=True).data,
            #                  'orders2': OrderSerializer(orders2, many=True).data,
            #                  'orders3': OrderSerializer(orders3, many=True).data,
            #                  'orders': OrderSerializer(orders, many=True).data})

            start = datetime.strptime(start, '%Y-%m-%d')
            end = datetime.strptime(end, '%Y-%m-%d')

            # for i in range(delta.days + 1):
            #     day = (start + timedelta(days=i)).date()
            #     str_day = str(day)
            #     temp1 = {'orders_list': [], 'order_count': 0, 'profit': 0}
            #     orders = Orders.objects.filter(Q(start__lte=day, end__gte=day), rent_id=rent_id)
            #     for order in orders:
            #         temp1['orders_list'].append(order.order_id)
            #         temp1['profit'] += float(order.car_id.rent_cost)
            #     temp1['order_count'] = len(temp1['orders_list'])
            #     temp.append({str_day: temp1})
            # return Response(temp)

            # return Response({'orders': OrderSerializer(orders, many=True).data})

            return self.get_order_helper(rent_id, start, end)

        elif start:
            orders = Orders.objects.filter(Q(start__lte=start, end__gte=start), rent_id=rent_id)
            temp1 = {'orders_list': [], 'order_count': 0, 'profit': 0}
            for order in orders:
                temp1['orders_list'].append(order.order_id)
                temp1['profit'] += float(order.car_id.rent_cost)
            temp1['order_count'] = len(temp1['orders_list'])
            return Response([temp1])

        elif days:
            end = datetime.today()
            start = end - timedelta(days=int(days))
            return self.get_order_helper(rent_id, start, end)

        return Response({}, status=status.HTTP_404_NOT_FOUND)

    # def get_cars(self, request):
    #     start = datetime.now()
    #     rent_id = Token.objects.get(key=request.user.auth_token).user.id
    #     cars = Cars.objects.filter(rent_id=rent_id).values_list('car_id', 'car_num', 'brand', 'model')
    #     result = [list(i) + [Orders.objects.filter(car_id=i[0]).count()] for i in cars]
    #     # for i in cars:
    #     #     result += [list(i) + [Orders.objects.filter(car_id=i[0]).count()]]
    #     print(datetime.now() - start)
    #     return Response(result)

    # def get_cash_flow(self, request):
    #     rent_id = Token.objects.get(key=request.user.auth_token).user.id
    #     days = request.GET.get('days')
    #     start = request.GET.get('start')
    #     end = request.GET.get('end')
    #     if start and end:
    #         pass
    #
    #     elif start:
    #         ...
    #
    #     elif days:
    #         if int(days) == 3:
    #             orders = Orders.objects.filter(rent_id=rent_id, )
    #
    #     return Response({})

    def get_top_clients(self, request):
        rent_id = Token.objects.get(key=request.user.auth_token).user.id
        clients = RentUsers.objects.filter(rent_id=rent_id)
        result = []
        for i in clients:
            data = i.client_id.__dict__
            orders = Orders.objects.filter(client_id=i.client_id, rent_id=rent_id).values_list('order_id', flat=True)
            data['order_count'] = len(orders)
            data['orders_list'] = orders
            result.append(TopClientsSerializer(data, many=False).data)
        # for i in clients:
        #     result[i.client_id.client_id] = Orders.objects.filter(client_id=i.client_id, rent_id=rent_id).values_list(
        #         'order_id', flat=True
        #     )
        result = sorted(result, key=lambda k: k['order_count'], reverse=True)
        return Response(result, status=status.HTTP_200_OK)

    def get_car_cashflow(self, request):
        rent_id = Token.objects.get(key=request.user.auth_token).user.id
        cars = Cars.objects.filter(rent_id=rent_id)
        result = []
        for i in cars:
            orders = Orders.objects.filter(car_id=i.car_id, rent_id=rent_id)
            temp = 0
            for j in orders:
                temp += (j.end - j.start).days
            data = i.__dict__
            data['payback'] = (temp * float(i.rent_cost)) / float(i.cost)
            data['profit'] = temp * float(i.rent_cost)
            data['orders_list'] = orders.values_list('order_id', flat=True)
            data['order_count'] = len(data['orders_list'])
            data['days'] = temp
            result.append(CarCashflowserializer(data).data)
            result = sorted(result, key=lambda k: k['profit'], reverse=True)
        return Response(result, status=status.HTTP_200_OK)

    def get(self, request, query):

        response = {
            'orders': self.get_orders,
            # 'cars': self.get_cars,
            # 'cashflow': self.get_cash_flow,
            'top_clients': self.get_top_clients,
            'car_cashflow': self.get_car_cashflow,
        }
        if query in response:
            return response.get(query)(request)
        return Response({}, status=status.HTTP_404_NOT_FOUND)