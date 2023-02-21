from django.contrib import admin

from .models import Client
from .models import Contractor
from .models import Order
from .models import Message

class OrderItemInline(admin.TabularInline):
    model = Order
    extra = 0


class OrderChatMessageInline(admin.TabularInline):
    model = Message


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['title', 'client', 'status', 'contractor']
    inlines = [
        OrderChatMessageInline
    ]


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    inlines = [
        OrderItemInline
    ]


@admin.register(Contractor)
class ContractorAdmin(admin.ModelAdmin):
    inlines = [
        OrderItemInline
    ]
