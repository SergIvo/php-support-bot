АПИ для сохранения данных заказчика - http://127.0.0.1:8000/api/create/
Пример вызова(POST):
```json
{"tariff": "VIP", "full_name": "Иван", "telegram_id": "234253453"}
```


АПИ для сохранения заказа -  http://127.0.0.1:8000/api/create
Пример вызова(POST):
```json
{"title": "СРОЧНО НУЖЕН САЙТ", "telegram_id": "4324234"}
```
АПИ возвращает все заказы клиента:#TODO
