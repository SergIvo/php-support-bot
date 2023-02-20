АПИ для сохранения данных заказчика - api/register/

Пример вызова(POST):
```json
{"tariff": "VIP", "full_name": "Иван", "telegram_id": "234253453"}
```
АПИ для сохранения заказа -  order/create/

Пример вызова(POST): 
```json
{"title": "СРОЧНО НУЖЕН САЙТ", "telegram_id": "4324234"}
```
АПИ возвращает(GET) заказ или обновляет(PUT) по номеру id:
```
api/order/get_or_update/id
```
АПИ возвращает(GET) все связанные заказы юзера:
```
api/orders/telegram_id
```
