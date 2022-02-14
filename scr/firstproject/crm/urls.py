from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .APIviews import RentUserList, RentList, LoginView, Logout, FileDownloadListAPIView, scheduledtask
from .views.viewfortgbot import viewforbot, ConfirmApplications
from .views.analytics import Analytics
from .views.blacklist import ClientInfoFromBlackList
from .views.cars import CarList, CarFilter, BrandAndModelView
from .views.clients import ClientsList
from .views.orders import OrderList, ExtendedOrder
from .views.users import UserList

router = DefaultRouter()

router.register('cars', CarList, basename='cars')
router.register('clients', ClientsList, basename='clients')
router.register('orders', OrderList, basename='orders')
router.register('rent_users', RentUserList, basename='rent_users')
router.register('users', UserList, basename='users')
router.register('rents', RentList, basename='rents')
router.register('black_list', ClientInfoFromBlackList, basename='blacklist')
router.register('clients_tg', ConfirmApplications, basename='clients_tg')
router.register('extended_order', ExtendedOrder, basename='extended_order')

urlpatterns = [
    path('', include(router.urls)),
    path('logout/', Logout.as_view(), name='logout1'),
    path('login/', LoginView.as_view(), name='login1'),
    path('brand&model/', BrandAndModelView.as_view(), name='brand&model'),
    path('available/cars', CarFilter.as_view(), name='car_filter'),
    path('getfile', FileDownloadListAPIView.as_view(), name='getfile'),
    path('analytics/<str:query>/', Analytics.as_view(), name='analytics'),
    path('bot/', viewforbot, name='viewforbot'),
    path('task/', scheduledtask, name='scheduledtask'),
]
