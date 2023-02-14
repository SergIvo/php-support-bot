from django.contrib import admin

from .models import Client
from .models import Contractor
from .models import Order

class OrderItemInline(admin.TabularInline):
    model = Order
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    pass


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
