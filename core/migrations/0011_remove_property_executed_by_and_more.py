# Generated by Django 5.1.7 on 2025-05-19 12:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_property_latitude_property_longitude'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='property',
            name='executed_by',
        ),
        migrations.RemoveField(
            model_name='property',
            name='reserved_by',
        ),
        migrations.AlterField(
            model_name='property',
            name='latitude',
            field=models.FloatField(blank=True, null=True, verbose_name='خط العرض'),
        ),
        migrations.AlterField(
            model_name='property',
            name='longitude',
            field=models.FloatField(blank=True, null=True, verbose_name='خط الطول'),
        ),
    ]
