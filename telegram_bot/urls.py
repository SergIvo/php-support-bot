from .views import register_client, create_order, get_order
from django.urls import path

urlpatterns = [
    path('register/', register_client),
    path('create/', create_order),
    path('orders/', get_order)
]

