from django.contrib import admin
from django.db import router
from django.urls import path ,include
from rest_framework import routers
from store.api import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('Customer',views.Customerview,basename='Customerview')
router.register('Product',views.Productview,basename='Productview')
router.register('Order',views.Orderview,basename='Orderview')
router.register('OrderItem',views.OrderItemview,basename='OrderItemview')
router.register('ShippingAddress',views.ShippingAddressview,basename='ShippingAddressview')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    #path('auth/',include('rest_framework.urls',namespace='rest_framework')

]