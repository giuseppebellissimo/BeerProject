from django.contrib.auth.models import User
from django.db import models
from django.db.models import JSONField


# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    id_category = models.ForeignKey(Category, on_delete=models.CASCADE)
    property = JSONField()

    def __str__(self):
        return self.id_category


class Recipe(models.Model):
    name = models.CharField(max_length=200)
    litre = models.DecimalField(decimal_places=2, max_digits=10)
    ebc = models.DecimalField(decimal_places=2, max_digits=10)
    ibu = models.DecimalField(decimal_places=2, max_digits=10)
    id_user = models.ForeignKey(User, on_delete=models.CASCADE)
    ingredients = models.ManyToManyField(Ingredient, through='IngredientRecipe')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Recipe'
        verbose_name_plural = "Recipes"


class Inventory(models.Model):
    id_user = models.ManyToManyField(User)
    last_update = models.DateTimeField(auto_now=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    ingredients = models.ManyToManyField(Ingredient, through='InventoryIngredient')

    def __str__(self):
        return f'Inventory of {''.join(str(Users.username) for Users in self.id_user.all())}'

    class Meta:
        verbose_name = 'Inventory'
        verbose_name_plural = 'Inventories'
        ordering = ['-creation_date']


class Step(models.Model):
    id_recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)


class IngredientRecipe(models.Model):
    id_recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    id_ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.DecimalField(decimal_places=2, max_digits=10)
    measurement_unit = models.CharField(max_length=50)


class InventoryIngredient(models.Model):
    id_ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    id_inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE)
    quantity = models.DecimalField(decimal_places=2, max_digits=10)
    measurement_unit = models.CharField(max_length=100)
    expiry_date = models.DateField()
