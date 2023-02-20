from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Client, Order
from rest_framework.serializers import ModelSerializer
from django.urls import reverse
from django.http import HttpResponseRedirect
from rest_framework import generics


def redirect2admin(request):
    return HttpResponseRedirect(reverse('admin:index'))


class ClientSerializer(ModelSerializer):
    class Meta:
        model = Client
        fields = ['id', 'tariff', 'full_name', 'telegram_id']
        read_only_fields = ['id']


class OrderSerializer(ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'title', 'registered_at', 'client', 'contractor']
        read_only_fields = ['id', 'client']


@api_view(['POST'])
def register_client(request):
    received_client = request.data
    serializer = ClientSerializer(data=received_client)
    serializer.is_valid(raise_exception=True)
    client = Client.objects.create(
        tariff=received_client['tariff'],
        full_name=received_client['full_name'],
        telegram_id=received_client['telegram_id']
    )
    serializer = ClientSerializer(client)
    return Response(serializer.data)


@api_view(['POST'])
def create_order(request):
    received_order = request.data
    serializer = OrderSerializer(data=received_order)
    serializer.is_valid(raise_exception=True)
    client = Client.objects.get(telegram_id=received_order['telegram_id'])
    order = Order.objects.create(
        title = received_order['title'],
        client = client
    )
    serializer = OrderSerializer(order)
    return Response(serializer.data)

class OrderAPIUpdate(generics.RetrieveUpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer


@api_view(['GET'])
def get_orders(request, tg_id):
    client = Client.objects.get(telegram_id=tg_id)
    orders = client.orders.all()
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)
