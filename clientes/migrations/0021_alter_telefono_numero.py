# Generated by Django 5.1.1 on 2024-11-03 03:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clientes', '0020_remove_cliente_telefono_telefono'),
    ]

    operations = [
        migrations.AlterField(
            model_name='telefono',
            name='numero',
            field=models.CharField(blank=True, max_length=50),
        ),
    ]
