from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save, post_delete
from django.conf import settings
from django.dispatch import receiver
from django.shortcuts import get_object_or_404
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from rest_framework.authtoken.views import Token
from urllib.request import urlopen


def clients_dir_path(instance, filename):
    extension = filename.split('.')[-1]
    new_filename = "clients/{}.{}".format(instance.passport_series, extension)
    return new_filename


def cars_dir_path(instance, filename):
    extension = filename.split('.')[-1]
    new_filename = "cars/{}-{}-{}.{}".format(instance.brand, instance.model, instance.car_num, extension)
    return new_filename


class Clients(models.Model):
    client_id = models.AutoField(primary_key=True, unique=True, auto_created=True)
    passport_series = models.CharField(unique=True, max_length=20)
    firstname = models.CharField(max_length=150)
    lastname = models.CharField(max_length=150)
    second_name = models.CharField(max_length=150)
    date_of_birth = models.DateField()
    date_of_issue = models.DateField()
    issued = models.CharField(max_length=250)
    address = models.CharField(max_length=250)
    phone = models.CharField(max_length=20)
    in_black_list = models.BooleanField(default=False)
    photo = models.ImageField(upload_to=clients_dir_path, null=True, blank=True)
    status = models.CharField(max_length=30, default='vacant')

    class Meta:
        verbose_name = "Client"
        verbose_name_plural = "Clients"

    def __str__(self):
        return f"{self.firstname} {self.lastname} {self.passport_series}"

    def get_image_from_url(self, url):
        img_tmp = NamedTemporaryFile(delete=True)
        with urlopen(url) as uo:
            assert uo.status == 200
            img_tmp.write(uo.read())
            img_tmp.flush()
        img = File(img_tmp)
        extension = url.split('.')[-1]
        self.photo.save('base.{}'.format(extension), img)


class User(AbstractUser):
    is_superuser = models.BooleanField()
    is_rent = models.BooleanField(default=False)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"


class Rent(models.Model):
    # Над доработать эту таблицу
    rent_id = models.OneToOneField(User, primary_key=True, unique=True, on_delete=models.CASCADE)
    rent_name = models.CharField(max_length=50, null=True)
    rent_phone_no = models.CharField(max_length=20, null=True)
    document_num = models.IntegerField(null=True)
    bot_token = models.CharField(null=True, blank=True, max_length=200)
    url_token = models.CharField(null=True, blank=True, max_length=100)
    order_number = models.IntegerField(default=1)

    class Meta:
        verbose_name = "Rent"
        verbose_name_plural = "Rents"

    # def __str__(self):
    #     return f"{self.rent_name} {self.rent_id.username}"


class SuperUser(models.Model):
    user = models.OneToOneField(User, primary_key=True, unique=True, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "SuperUser"
        verbose_name_plural = "SuperUsers"


class Cars(models.Model):
    car_id = models.AutoField(primary_key=True, unique=True, auto_created=True)
    rent_id = models.ForeignKey(Rent, on_delete=models.CASCADE)
    brand = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    color = models.CharField(max_length=50)
    cost = models.CharField(max_length=12)
    engine_num = models.CharField(unique=True, max_length=50)
    body_num = models.CharField(max_length=50)
    tech_passport = models.CharField(unique=True, max_length=12)
    car_num = models.CharField(unique=True, max_length=12)
    spare_wheel = models.CharField(max_length=150, default=None)
    battery = models.CharField(max_length=100, default=None)
    wheels_model = models.CharField(max_length=100, default=None)
    status = models.CharField(max_length=20, default="vacant")
    rent_cost = models.CharField(max_length=12)
    photo = models.ImageField(upload_to=cars_dir_path, null=True, blank=True)
    toning = models.CharField(max_length=20, default="без тонировки")
    year_of_issue = models.CharField(max_length=10, null=True, blank=True)

    class Meta:
        verbose_name = "Car"
        verbose_name_plural = "Cars"

    def __str__(self):
        return f"{self.brand} {self.model} {self.car_num}"


class Orders(models.Model):
    order_id = models.AutoField(primary_key=True, unique=True, auto_created=True)
    rent_id = models.ForeignKey(Rent, on_delete=models.SET_NULL, null=True)
    client_id = models.ForeignKey(Clients, on_delete=models.CASCADE)
    car_id = models.ForeignKey(Cars, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    start = models.DateField()
    end = models.DateField()
    status = models.CharField(max_length=30, default="in progress")
    start_time = models.TimeField(blank=True, null=True)
    end_time = models.TimeField(blank=True, null=True)
    order_number = models.IntegerField(blank=True, null=True)
    is_extended = models.BooleanField(default=False)
    extended_to = models.DateField(blank=True, null=True)

    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"

    def __int__(self):
        return self.order_id


class OrderInformation(models.Model):
    order_id = models.ForeignKey(Orders, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    from_date = models.DateField(blank=True, null=True)
    to_date = models.DateField()
    from_time = models.TimeField(blank=True, null=True)
    to_time = models.TimeField()
    order_number = models.IntegerField(null=True, blank=True)

    class Meta:
        verbose_name = "OrderInformation"
        verbose_name_plural = "OrdersInformation"

    def __int__(self):
        return self.order_id


class RentUsers(models.Model):
    # Над доработать эту таблицу
    rent_id = models.ForeignKey(Rent, on_delete=models.CASCADE)
    client_id = models.ForeignKey(Clients, on_delete=models.CASCADE)
    moved_from = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_created=True, auto_now_add=True)

    class Meta:
        verbose_name = "RentUser"
        verbose_name_plural = "RentUsers"


class BlackList(models.Model):
    client_id = models.OneToOneField(Clients, primary_key=True, on_delete=models.CASCADE)
    rent_id = models.ForeignKey(Rent, on_delete=models.CASCADE)
    description = models.CharField(max_length=250, default="This is bad client")
    timestamp = models.DateTimeField(auto_now_add=True)

    def get_rent_id(self):
        return self.rent_id.rent_id.id

    class Meta:
        verbose_name = "BlackList"
        verbose_name_plural = "BlackList"


class ClientsFromTg(models.Model):
    client_id = models.AutoField(primary_key=True, unique=True, auto_created=True)
    rent_id = models.ForeignKey(Rent, on_delete=models.CASCADE)
    passport_series = models.CharField(unique=True, max_length=10)
    firstname = models.CharField(max_length=150)
    lastname = models.CharField(max_length=150)
    second_name = models.CharField(max_length=150)
    date_of_birth = models.DateField()
    date_of_issue = models.DateField()
    issued = models.CharField(max_length=250)
    address = models.CharField(max_length=250)
    phone = models.CharField(max_length=20)
    photo = models.URLField(blank=True, null=True)
    chat_id = models.CharField(max_length=20)

    class Meta:
        verbose_name = "ClientFromTg"
        verbose_name_plural = "ClientsFromTg"

    def get_rent_id(self):
        return self.rent_id.rent_id.id


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


@receiver(post_delete, sender=settings.AUTH_USER_MODEL)
def delete_auth_token(sender, instance=None, deleted=False, **kwargs):
    if deleted:
        Token.objects.delete(user=instance)


@receiver(post_save, sender=BlackList)
def update_user(sender, instance=None, created=False, **kwargs):
    if created:
        client = get_object_or_404(Clients, client_id=instance.client_id.client_id)
        client.in_black_list = True
        client.save()


@receiver(post_delete, sender=BlackList)
def update_user_info(sender, instance=None, **kwargs):
    # if deleted:
    client = get_object_or_404(Clients, pk=instance.client_id.client_id)
    client.in_black_list = False
    client.save()


@receiver(post_save, sender=Orders)
def update_car_status(sender, instance=None, created=False, **kwargs):
    if created:
        rent = get_object_or_404(Rent, pk=instance.rent_id)
        order = get_object_or_404(Orders, pk=instance.order_id)
        order.order_number = rent.order_number
        rent.order_number = rent.order_number + 1
        car = get_object_or_404(Cars, pk=instance.car_id.car_id)
        client = get_object_or_404(Clients, pk=instance.client_id.client_id)
        car.status = "occupied"
        client.status = "occupied"
        rent.save()
        order.save()
        car.save()
        client.save()


@receiver(post_save, sender=OrderInformation)
def update_order(sender, instance=None, created=False, **kwargs):
    if created:
        order = get_object_or_404(Orders, pk=instance.order_id)
        rent = get_object_or_404(Rent, pk=instance.order_id.rent_id)
        extendedorder = get_object_or_404(OrderInformation, order_id=instance.order_id, pk=instance.id)
        extendedorder.order_number = rent.order_number
        rent.order_number = rent.order_number + 1
        order.is_extended = True
        if order.extended_to:
            extendedorder.from_date = order.extended_to
        else:
            extendedorder.from_date = order.end
        order.extended_to = extendedorder.to_date
        extendedorder.from_time = order.end_time
        order.save()
        rent.save()
        extendedorder.save()
