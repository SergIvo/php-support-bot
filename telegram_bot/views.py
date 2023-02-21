from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Client, Order, Message
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
        fields = ['id', 'title', 'registered_at', 'client', 'description', 'contractor', 'status']
        read_only_fields = ['id', 'client']


class MessageSerializer(ModelSerializer):
    class Meta:
        model = Message
        fields = ['sender', 'order', 'text']
        read_only_fields = ['id']


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
    print(serializer.validated_data)
    client = Client.objects.get(telegram_id=received_order['telegram_id'])
    order = Order.objects.create(
        title=serializer.validated_data['title'],
        description=received_order['description'],
        client=client
    )
    serializer = OrderSerializer(order)
    return Response(serializer.data)

class OrderAPIUpdate(generics.RetrieveUpdateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer


@api_view(['POST'])
def create_message(request):
    received_message = request.data
    serializer = MessageSerializer(data=received_message)
    serializer.is_valid(raise_exception=True)
    message = Message.objects.create(
        sender=serializer.validated_data['sender'],
        order=serializer.validated_data['order'],
        text=serializer.validated_data['text']
    )
    serializer = MessageSerializer(message)
    return Response(serializer.data)


@api_view(['GET'])
def get_orders(request, tg_id):
    client = Client.objects.get(telegram_id=tg_id)
    orders = client.orders.all()
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def get_new_orders(request):
    orders = Order.objects.filter(status='NOT_ASSIGNED')
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)



@api_view(['GET'])
def get_chat_messages(request, order_id):
    order = Order.objects.get(id=order_id)
    messages = order.messages.all()
    serializer = MessageSerializer(messages, many=True)
    return Response(serializer.data)
