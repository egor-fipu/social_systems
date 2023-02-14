from django.db.models import Sum, Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from .mixins import ListRetrieveViewSet, ListViewSet
from .models import Restaurant, Basket, Position, Order
from .serializers import (RestaurantSerializer, BasketSerializer,
                          AddPositionSerializer, OrderSerializer)


class RestaurantViewSet(ListRetrieveViewSet):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('id', 'name')


class BasketViewSet(ListViewSet):
    serializer_class = AddPositionSerializer

    def list(self, request, *args, **kwargs):
        """Просмотр корзины"""
        queryset = Basket.objects.prefetch_related('positions__dish').filter(
            user=request.user).annotate(Sum('positions__price')).first()
        serializer = BasketSerializer(queryset)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='add')
    def add_position(self, request):
        """Добавление блюда в корзину. Если такое блюдо уже есть в корзине,
        то его количество суммируется."""
        serializer = AddPositionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        position, created = Position.objects.get_or_create(
            dish=serializer.validated_data['dish_id'],
            basket=request.user.basket
        )
        if created:
            position.quantity = serializer.validated_data['quantity']
        else:
            position.quantity += serializer.validated_data['quantity']
        position.price = position.quantity * serializer.validated_data[
            'dish_id'].price
        position.save(update_fields=('quantity', 'price'))

        return Response(status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='delete')
    def delete_position(self, request):
        """Удаление блюда из корзины."""
        serializer = AddPositionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        position = Position.objects.filter(
            dish=serializer.validated_data['dish_id'],
            basket=request.user.basket
        ).first()
        if not position:
            return Response(
                {'error': f'Блюда "dish_id"='
                          f'{serializer.validated_data["dish_id"].id} '
                          f'нет в вашей корзине.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if position.quantity == serializer.validated_data['quantity']:
            position.delete()
        elif position.quantity < serializer.validated_data['quantity']:
            return Response(
                {'error': f'Можно удалить максимум {position.quantity} единиц '
                          f'этого блюда из вашей корзины.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        else:
            position.quantity -= serializer.validated_data['quantity']
            position.price = position.quantity * serializer.validated_data[
                'dish_id'].price
            position.save(update_fields=('quantity', 'price'))

        return Response(status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='pay')
    def pay_positions(self, request):
        """Оплата корзины."""
        positions_qs = Position.objects.filter(basket__user=request.user)
        total_price = positions_qs.aggregate(Sum('price'))

        if not total_price['price__sum']:
            return Response(
                {'error': f'В вашей корзине нет позиций для оплаты.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if request.user.wallet < total_price['price__sum']:
            return Response(
                {'error': f'На вашем счете недостаточно средств для оплаты '
                          f'корзины.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        # списываем деньги с кошелька
        request.user.wallet -= total_price['price__sum']
        request.user.save(update_fields=('wallet',))
        # создаем заказ
        order_obj = Order.objects.create(user=request.user)
        # перемещаем позиции из корзины в заказ
        positions_qs.update(basket=None, order=order_obj)

        return Response(status=status.HTTP_200_OK)


class OrderViewSet(ListViewSet):

    def list(self, request, *args, **kwargs):
        """Просмотр заказов"""
        queryset = Order.objects.prefetch_related(
            'positions__dish').filter(
            user=self.request.user).annotate(Sum('positions__price')).order_by(
            '-created_at')[:10]
        totals = Order.objects.filter(
            user=self.request.user).aggregate(
            Count('id', distinct=True), Sum('positions__price')
        )
        serializer = OrderSerializer(queryset, many=True)

        out_data = {
            'total_count': totals['id__count'],
            'total_sum': totals['positions__price__sum'],
            'last_orders': serializer.data
        }

        return Response(out_data, status=status.HTTP_200_OK)
