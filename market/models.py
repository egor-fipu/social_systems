from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save


class User(AbstractUser):
    wallet = models.FloatField('Виртуальный кошелек', default=0)

    # basket
    # orders

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['-date_joined']

    def __str__(self):
        return f'{self.username} ({self.last_name})'


def post_save_user(sender, **kwargs):
    """После создания юзера - создаем ему корзину"""
    if kwargs['created']:
        user = kwargs['instance']
        Basket.objects.create(user=user)


post_save.connect(post_save_user, sender=User)


class Restaurant(models.Model):
    name = models.CharField('Название', max_length=100)

    # dishes

    class Meta:
        verbose_name = 'Ресторан'
        verbose_name_plural = 'Рестораны'
        ordering = ['id']

    def __str__(self):
        return self.name


class Dish(models.Model):
    name = models.CharField('Название', max_length=100)
    price = models.FloatField('Стоимость')
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name='dishes',
        verbose_name='Ресторан'
    )

    # positions

    class Meta:
        verbose_name = 'Блюдо'
        verbose_name_plural = 'Блюда'
        ordering = ['id']

    def __str__(self):
        return self.name


class Basket(models.Model):
    """Корзина"""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='basket',
        verbose_name='Пользователь'
    )
    dishes = models.ManyToManyField(
        Dish,
        through='Position',
        related_name='baskets',
        verbose_name='Блюда'
    )

    # positions

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'
        ordering = ['-id']

    def __str__(self):
        return self.user.username


class Order(models.Model):
    """Заказ"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name='Пользователь'
    )
    dishes = models.ManyToManyField(
        Dish,
        through='Position',
        related_name='orders',
        verbose_name='Блюда'
    )
    created_at = models.DateTimeField('Время создания', auto_now_add=True)

    # positions

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-id']

    def __str__(self):
        return self.user.username


class Position(models.Model):
    """Блюдо в корзине/заказе конкретного пользователя"""
    dish = models.ForeignKey(
        Dish, on_delete=models.CASCADE, related_name='positions'
    )
    basket = models.ForeignKey(
        Basket, on_delete=models.CASCADE, related_name='positions',
        blank=True, null=True
    )
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name='positions',
        blank=True, null=True
    )
    quantity = models.PositiveSmallIntegerField('Количество', default=1)
    price = models.FloatField('Стоимость', default=0)

    class Meta:
        verbose_name = 'Блюдо в Корзине (Позиция)'
        verbose_name_plural = 'Блюда в Корзине (Позиции)'
        ordering = ['-id']
        constraints = [
            models.UniqueConstraint(
                fields=['dish', 'basket'],
                name='unique_dish_basket'
            ),
            models.UniqueConstraint(
                fields=['dish', 'order'],
                name='unique_dish_order'
            ),
        ]

    def __str__(self):
        return f'{self.dish.name} ({self.basket.user.username})'
