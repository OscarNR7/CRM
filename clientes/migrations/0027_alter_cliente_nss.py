# Generated by Django 5.1.1 on 2024-11-15 19:33

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clientes', '0026_cliente_cambio_de_afore_cliente_foto_aval'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cliente',
            name='nss',
            field=models.CharField(help_text='Número de Seguridad Social (NSS)', max_length=100, unique=True, validators=[django.core.validators.RegexValidator(message='El NSS solo debe contener números.', regex='^\\d+$')]),
        ),
    ]