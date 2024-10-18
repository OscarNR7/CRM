# Generated by Django 5.1.1 on 2024-10-18 22:58

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clientes', '0011_rename_semanacliente_pago'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pago',
            name='semana',
        ),
        migrations.RemoveField(
            model_name='pago',
            name='vendedor',
        ),
        migrations.AddField(
            model_name='pago',
            name='observaciones',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='pago',
            name='anticipo',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
        migrations.AlterField(
            model_name='pago',
            name='cancelacion',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='pago',
            name='cantidad',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
        migrations.AlterField(
            model_name='pago',
            name='cliente',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pagos', to='clientes.cliente'),
        ),
        migrations.AlterField(
            model_name='pago',
            name='porcentaje',
            field=models.DecimalField(decimal_places=2, max_digits=5),
        ),
    ]