# Generated by Django 5.1.1 on 2024-10-18 23:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clientes', '0012_remove_pago_semana_remove_pago_vendedor_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pago',
            name='cancelacion',
            field=models.TextField(blank=True, null=True),
        ),
    ]
