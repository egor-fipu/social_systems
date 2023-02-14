from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (RestaurantViewSet, BasketViewSet, OrderViewSet)

router_v1 = DefaultRouter()

router_v1.register(r'restaurants', RestaurantViewSet, basename='restaurants')
router_v1.register(r'basket', BasketViewSet, basename='basket')
router_v1.register(r'orders', OrderViewSet, basename='orders')

urlpatterns = [
    path('', include(router_v1.urls)),
]
