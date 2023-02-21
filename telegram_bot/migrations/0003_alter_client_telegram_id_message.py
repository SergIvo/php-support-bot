# Generated by Django 4.1.7 on 2023-02-14 22:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('telegram_bot', '0002_alter_order_contractor'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='telegram_id',
            field=models.IntegerField(blank=True, db_index=True, null=True, unique=True, verbose_name='Telegram Id'),
        ),
    ]
