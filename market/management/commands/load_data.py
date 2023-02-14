import csv

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from market.models import Restaurant, Dish

User = get_user_model()


class Command(BaseCommand):

    def handle(self, *args, **options):
        counter = 0
        user = User.objects.filter(username='test_user').first()
        if not user:
            user = User.objects.create_user(
                username='test_user', wallet=100000
            )
            user.set_password('test_password')
            user.save()
            counter += 1

        with open('market/static/data/restaurants.csv', newline='',
                  encoding='windows-1251') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=';')
            for row in reader:
                _, created = Restaurant.objects.get_or_create(**row)
                if created:
                    counter += 1

        with open('market/static/data/dishes.csv', newline='',
                  encoding='windows-1251') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=';')
            for row in reader:
                _, created = Dish.objects.get_or_create(**row)
                if created:
                    counter += 1

        self.stdout.write(self.style.SUCCESS(f'В БД создано {counter} записей'))
