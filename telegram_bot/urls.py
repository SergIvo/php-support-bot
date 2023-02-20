from .views import *
from django.urls import path

urlpatterns = [
    path('register/', register_client),
    path('order/create/', create_order),
    path('order/get_or_update/<int:pk>', OrderAPIUpdate.as_view()),
    path('user/orders/<int:tg_id>', get_orders)
]

