# Generated by Django 5.0.2 on 2024-05-01 16:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('beerRecipe', '0014_ingredientrecipe_original_unit'),
    ]

    operations = [
        migrations.AddField(
            model_name='ingredient',
            name='producer',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
