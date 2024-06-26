# Generated by Django 5.0.2 on 2024-04-03 08:50

import django_yaml_field.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('beerRecipe', '0011_alter_step_options_inventory_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='ingredient',
            name='comment',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='inventory',
            name='is_default',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='inventoryingredient',
            name='original_unit',
            field=models.CharField(default=None, max_length=10),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='ingredient',
            name='property',
            field=django_yaml_field.fields.YAMLField(blank=True),
        ),
    ]
