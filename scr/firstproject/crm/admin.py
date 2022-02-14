from django.contrib import admin

# Register your models here.
from .models import *
#
# admin.site.register(Users)
# # admin.site.register(Clients)
# admin.site.register(Rent)
# admin.site.register(Cars)
# admin.site.register(Orders)
# admin.site.register(Rent_Users)


@admin.register(Clients)
class UserModel(admin.ModelAdmin):
    list_display = ('client_id', 'passport_series', 'firstname', 'lastname', 'photo', 'in_black_list')


@admin.register(User)
class UserModel(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name', 'is_superuser', 'is_rent')


@admin.register(SuperUser)
class UserModel(admin.ModelAdmin):
    list_display = ('user',)


@admin.register(Rent)
class UserModel(admin.ModelAdmin):
    list_display = ('rent_id', 'rent_name', 'rent_phone_no')


@admin.register(Cars)
class UserModel(admin.ModelAdmin):
    list_display = ('car_id', 'brand', 'model', 'color', 'status', 'cost', 'rent_cost', 'photo')


@admin.register(Orders)
class UserModel(admin.ModelAdmin):
    list_display = ('order_id',  'client_id', 'car_id', 'timestamp', 'status', 'start', 'end')


@admin.register(RentUsers)
class UserModel(admin.ModelAdmin):
    list_display = ('rent_id', 'client_id')


@admin.register(BlackList)
class UserModel(admin.ModelAdmin):
    list_display = ('client_id', 'description', 'timestamp')


@admin.register(ClientsFromTg)
class UserModel(admin.ModelAdmin):
    list_display = ('client_id',)


@admin.register(OrderInformation)
class OrderInfo(admin.ModelAdmin):
    list_display = ('order_id', 'from_date', 'from_time', 'to_date', 'to_time', 'timestamp')
