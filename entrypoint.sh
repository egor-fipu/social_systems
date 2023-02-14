#!/bin/sh

python manage.py migrate
python manage.py load_data
python manage.py runserver 0:8000