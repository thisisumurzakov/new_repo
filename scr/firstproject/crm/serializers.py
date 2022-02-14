from datetime import datetime

from rest_framework import serializers

from .models import Cars, Clients, Orders, RentUsers, User, Rent, BlackList, ClientsFromTg, OrderInformation


class CarSerializer(serializers.ModelSerializer):
    photo = serializers.ImageField(required=False)

    class Meta:
        model = Cars
        fields = "__all__"

        extra_kwargs = {'rent_id': {
            'write_only': True,
            'required': False
        },
        }

    def validate_cost(self, value):
        if not(value.isnumeric()):
            raise serializers.ValidationError("Cost of car must be numeric value")
        return value

    def validate_rent_cost(self, value):
        if not(value.isnumeric()):
            raise serializers.ValidationError("The car rental price must be a numerical value.")
        return value


class ClientSerializer(serializers.ModelSerializer):
    photo = serializers.ImageField(required=False)
    date_of_birth = serializers.DateField(input_formats=['%Y-%m-%d'])
    date_of_issue = serializers.DateField(input_formats=['%Y-%m-%d'])

    class Meta:
        model = Clients
        fields = ['client_id', 'passport_series', 'firstname', 'lastname', 'second_name', 'date_of_birth',
                  'date_of_issue', 'issued', 'address', 'phone', 'in_black_list', 'photo', 'status']

    def validate_passport_series(self, value):
        if len(value.strip()) not in [9, 15]:
            raise serializers.ValidationError(
                "The length of the passport series must be 9 or Length of id number should be 15"
            )
        return value

    def validate_phone(self, value):
        if len(value.strip()) != 9:
            raise serializers.ValidationError("The length of phone number with out (+998) must be equal 9")
        return value


class OrderInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderInformation
        fields = "__all__"

    def validate_to_date(self, value):
        data = self.get_initial()
        order_id = data.get('order_id')
        order = Orders.objects.get(pk=order_id)
        to_date = datetime.strptime(data.get('to_date'), '%Y-%m-%d').date()
        if order.is_extended:
            if order.extended_to <= to_date:
                return value
            else:
                raise serializers.ValidationError(
                    "To_date must be greater than order extended_to !!!"
                )
        elif order.end <= to_date:
            return value
        else:
            raise serializers.ValidationError(
                "To_date must be greater than order end date!!!"
            )


class OrderSerializer(serializers.ModelSerializer):
    start = serializers.DateField(format='%d-%B-%Y', input_formats=['%Y-%m-%d'])
    end = serializers.DateField(format='%d-%B-%Y', input_formats=['%Y-%m-%d'])
    firstname = serializers.CharField(source='client_id.firstname', required=False, read_only=True)
    lastname = serializers.CharField(source='client_id.lastname', required=False, read_only=True)
    passport = serializers.CharField(source='client_id.passport_series', required=False, read_only=True)
    client_photo = serializers.CharField(source='client_id.photo', required=False, read_only=True)
    client_phone = serializers.CharField(source='client_id.phone', required=False, read_only=True)
    brand = serializers.CharField(source='car_id.brand', required=False, read_only=True)
    model = serializers.CharField(source='car_id.model', required=False, read_only=True)
    car_photo = serializers.CharField(source='car_id.photo', required=False, read_only=True)
    car_num = serializers.CharField(source='car_id.car_num', required=False, read_only=True)

    class Meta:
        model = Orders
        fields = ('order_id', 'rent_id', 'client_id', 'car_id', 'timestamp', 'start', 'end', 'status',
                  'start_time', 'end_time', 'order_number',
                  'firstname', 'lastname', 'passport', 'client_photo', 'brand', 'model', 'car_photo', 'car_num',
                  'is_extended', 'extended_to', 'client_phone')

    extra_kwargs = {'rent_id': {
        'write_only': True,
        'required': False
    },
        'client_id': {
                'required': True
                },
        'car_id': {
            'required': True
        }
    }

    # def validate(self, data):
    #     start = data.get('start')
    #     end = data.get('end')
    #     if start >= end:
    #         raise serializers.ValidationError("start date must be lower than end date!!!")
    #     return data

    def validate_start(self, value):
        data = self.get_initial()
        end = datetime.strptime(data.get('end'), '%Y-%m-%d').date()
        if end < value:
            raise serializers.ValidationError(
                "start date must be lower than end date!!!"
            )
        return value

    def validate_end(self, value):
        data = self.get_initial()
        start = datetime.strptime(data.get('end'), '%Y-%m-%d').date()
        if value < start:
            raise serializers.ValidationError(
                "start date must be lower than end date!!!"
            )
        return value


class RentUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = RentUsers
        fields = ['rent_id', 'client_id', 'moved_from']


class RentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rent
        fields = "__all__"


class BlackListSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlackList
        fields = "__all__"

    extra_kwargs = {'timestamp': {
        'write_only': True,
        'required': False
    },
        'rent_id': {
            'write_only': True,
            'required': False
        }
    }


class UserSerializer(serializers.ModelSerializer):
    rent_name = serializers.CharField(max_length=100, required=False)
    rent_phone_no = serializers.CharField(max_length=20, required=False)
    document_num = serializers.IntegerField(required=False)

    class Meta:
        model = User
        fields = ['id', 'username', 'password',   'first_name', 'last_name', 'is_rent', 'is_superuser',
                  'rent_name', 'rent_phone_no', 'document_num']

        extra_kwargs = {'password': {
            'write_only': True,
            'required': True
        },
            'is_superuser': {
                'write_only': True,
                'required': True
            },
            'is_rent': {
                'write_only': True,
                'required': True
            },
            'rent_name': {
                'required': False
            },
            'rent_phone_no': {
                'required': False
            },
            'document_num': {
            'required': False
            }
        }


class CarCashflowserializer(serializers.ModelSerializer, serializers.Serializer):
    payback = serializers.FloatField()
    order_count = serializers.IntegerField()
    orders_list = serializers.ListField()
    profit = serializers.FloatField()
    days = serializers.IntegerField()

    class Meta:
        model = Cars
        fields = ['car_id', 'brand', 'model', 'color', 'cost', 'engine_num', 'body_num', 'tech_passport',
                  'car_num', 'spare_wheel', 'battery', 'wheels_model', 'status', 'rent_cost', 'photo', 'payback',
                  'profit', 'days', 'order_count', 'orders_list']


class TopClientsSerializer(serializers.ModelSerializer, serializers.Serializer):
    order_count = serializers.IntegerField()
    orders_list = serializers.ListField()

    class Meta:
        model = Clients
        fields = ['client_id', 'passport_series', 'firstname', 'lastname', 'second_name', 'date_of_birth',
                  'date_of_issue', 'issued', 'address', 'phone', 'in_black_list', 'photo', 'order_count', 'orders_list']


class ClientsFromTgSerializer(serializers.ModelSerializer):
    photo = serializers.URLField()
    date_of_birth = serializers.DateField(input_formats=['%Y-%m-%d'])
    date_of_issue = serializers.DateField(input_formats=['%Y-%m-%d'])

    class Meta:
        model = ClientsFromTg
        fields = ['client_id', 'rent_id', 'passport_series', 'firstname', 'lastname', 'second_name', 'date_of_birth',
                  'date_of_issue', 'issued', 'address', 'phone', 'photo', 'chat_id']

        extra_kwargs = {'chat_id': {
            'write_only': False,
            }
        }
