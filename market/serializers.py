from rest_framework import serializers

from .models import Dish, Restaurant, Basket, Position, Order


class DishSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dish
        fields = ('id', 'name', 'price')


class RestaurantSerializer(serializers.ModelSerializer):
    dishes = DishSerializer(many=True)

    class Meta:
        model = Restaurant
        fields = ('id', 'name', 'dishes')


class PositionSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = Position
        fields = ('id', 'name', 'quantity', 'price')
        extra_kwargs = {
            'id': {'source': 'dish'},
        }

    def get_name(self, instance):
        return instance.dish.name


class BasketSerializer(serializers.ModelSerializer):
    total_price = serializers.FloatField(
        source='positions__price__sum', read_only=True
    )
    positions = PositionSerializer(many=True)

    class Meta:
        model = Basket
        fields = ('total_price', 'positions',)


class AddPositionSerializer(serializers.Serializer):
    dish_id = serializers.SlugRelatedField(
        slug_field='id', queryset=Dish.objects.all(), required=True
    )
    quantity = serializers.IntegerField(required=True)

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                {'error': 'Значение "quantity" не может быть меньше 1'}
            )
        return value


class OrderSerializer(serializers.ModelSerializer):
    price = serializers.FloatField(
        source='positions__price__sum', read_only=True
    )
    time = serializers.SerializerMethodField()
    positions = PositionSerializer(many=True)

    class Meta:
        model = Order
        fields = ('id', 'price', 'time', 'positions',)

    def get_time(self, instance):
        return round(instance.created_at.timestamp())
