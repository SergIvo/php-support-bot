from django.db import models
from django.utils import timezone


class Client(models.Model):
    TARIFF_CHOICES = [
        ('ECONOM', 'Экономный'),
        ('STANDARD', 'Стандартный'),
        ('VIP', 'VIP')
    ]

    tariff = models.CharField(
        'Тариф',
        db_index=True,
        max_length=20,
        choices=TARIFF_CHOICES

    )
    full_name = models.CharField(
        'Полное имя',
        max_length=200,
        blank=True,
    )
    telegram_id = models.IntegerField(
        'Telegram Id',
        db_index=True,
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = 'Заказчик'
        verbose_name_plural = 'Заказчики'

    def __str__(self):
        return self.full_name


class Contractor(models.Model):
    full_name = models.CharField(
        'Полное имя',
        max_length=200,
        blank=True,
    )
    telegram_id = models.IntegerField(
        'Telegram Id',
        db_index=True,
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = 'Исполнитель'
        verbose_name_plural = 'Исполнители'

    def __str__(self):
        return self.full_name


class Order(models.Model):
    title = models.CharField(
        'Название заказа',
         max_length=200
    )
    registered_at = models.DateTimeField(
        verbose_name='Дата создания заказа',
        default=timezone.now,
        db_index=True,
        null=True
    )
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        verbose_name='заказчик',
        related_name='orders'
    )
    contractor = models.ForeignKey(
        Contractor,
        on_delete=models.CASCADE,
        verbose_name='исполнитель',
        related_name='orders'
    )

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return self.title