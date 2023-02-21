from .views import *
from django.urls import path

urlpatterns = [
    path('register/', register_client),
    path('order/create/', create_order),
    path('order/get_or_update/<int:pk>', OrderAPIUpdate.as_view()),
    path('user/orders/<int:tg_id>', get_orders),
    path('order/get_new/', get_new_orders),
    path('message/get_all/<int:order_id>', get_chat_messages),
    path('message/create/', create_message),
]

