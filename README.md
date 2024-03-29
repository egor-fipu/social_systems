# social_systems

Небольшое веб-приложение для заказа еды (по типу Яндекс Еды / Delivery Club)

## Запуск на локальном сервере

1. Установить docker и docker-compose

Инструкция по установке доступна в официальной документации

2. В папке с проектом выполнить команду
```
docker-compose up
```

3. При запуске контейнера запускается менеджмент команда `python manage.py 
load_data`, которая загружает в БД тестовые данные, в т.ч. пользователя
```json
{
  "username": "test_user",
  "password": "test_password",
  "wallet": 100000
}
```

## Описание API
- Сервис доступен только для авторизированных пользователей. Если пользователь 
не авторизован - все запросы выдают 403
- Аутентификация через сессию джанги
- Ресурс доступен в браузере по адресу `http://127.0.0.1:8000/api/`.

### 0. Авторизация
По адресу `http://127.0.0.1:8000/api-auth/login`
```
Логин: `test_user`
Gароль `test_password`
```

### 1. Просмотр меню
GET-запрос `http://127.0.0.1:8000/api/restaurants/`. Во вкладке `Filters` можно
настроить фильтрацию блюд по названию и/или id ресторана через параметры запроса

Ответ
- 200
```json
[
    {
        "id": 1, # ID ресторана
        "name": "Русская кухня",
        "dishes": [
            {
                "id": 1, # ID блюда
                "name": "Блюдо 1",
                "price": 10.0
            },
            {
                "id": 2,
                "name": "Блюдо 2",
                "price": 20.0
            },
            ...
        ]
    },
    ...
]
```

### 2. Добавление блюда в корзину
POST-запрос `http://127.0.0.1:8000/api/basket/add/`
```json
{
    "dish_id": 1, # ID блюда
    "quantity": 2 # Кол-во позиций на добавление
}
```
Ответ
- 200

### 3. Удаление блюда из корзины
POST-запрос `http://127.0.0.1:8000/api/basket/delete/`. Если указанное блюдо
отсутствует в корзине или его количество недостаточно, то вернется ошибка.
```json
{
    "dish_id": 1, # ID блюда
    "quantity": 2 # Кол-во позиций на добавление
}
```
Ответ
- 200

### 4. Просмотр корзины
GET-запрос `http://127.0.0.1:8000/api/basket/`

Ответ
- 200
```json
{
    "total_price": 100.0, # общая стоимость корзины
    "positions": [
        {
            "id": 1,
            "name": "Блюдо 1",
            "quantity": 2,
            "price": 20.0 # суммарная стоимость за все позиции
        },
        {
            "id": 2,
            "name": "Блюдо 2",
            "quantity": 1,
            "price": 20.0
        },
        ...
    ]
}
```

### 5. Оплата корзины
GET-запрос `http://127.0.0.1:8000/api/basket/pay/`. Списывает с баланса 
пользователя стоимость корзины. Создает заказ с данными из корзины на момент оплаты.

Ответ
- 200

### 6. Просмотр заказов
GET-запрос `http://127.0.0.1:8000/api/orders/`. В списке last_orders 
отображаются последние 10 заказов

Ответ
- 200
```json
{
    "total_count": 4, # общее кол-во заказов
    "total_sum": 440.0, # общая сумма заказов
    "last_orders": [ # последние 10 заказов в порядке убывания
        {
            "id": 4,
            "price": 30.0,
            "time": 1676347146, # timestamp времени создания
            "positions": [
                {
                    "id": 1,
                    "name": "Блюдо 1",
                    "quantity": 1,
                    "price": 10.0
                },
              ...
            ]
        },
        ...
    ]
}
```

