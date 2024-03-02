from django.contrib.auth.models import User
from django.db import models
from django_yaml_field import YAMLField


# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"


class Ingredient(models.Model):
    name = models.CharField(max_length=100)
    id_category = models.ForeignKey(Category, on_delete=models.CASCADE)
    property = YAMLField()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Ingredients"


class Recipe(models.Model):
    name = models.CharField(max_length=200)
    litre = models.DecimalField(decimal_places=2, max_digits=10)
    ebc = models.DecimalField(decimal_places=2, max_digits=10)
    ibu = models.DecimalField(decimal_places=2, max_digits=10)
    id_user = models.ForeignKey(User, on_delete=models.CASCADE)
    ingredients = models.ManyToManyField(Ingredient, through='IngredientRecipe')

    def __str__(self):
        return f'{self.name} - {self.litre} - {self.ebc} - {self.ibu}'

    class Meta:
        verbose_name_plural = "Recipes"


class Inventory(models.Model):
    id_user = models.ManyToManyField(User)
    last_update = models.DateTimeField(auto_now=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    ingredients = models.ManyToManyField(Ingredient, through='InventoryIngredient')

    def __str__(self):
        return f'Inventory of {''.join(str(Users.username) for Users in self.id_user.all())}'

    class Meta:
        verbose_name_plural = 'Inventories'
        ordering = ['-creation_date']


class Step(models.Model):
    id_recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    index = models.IntegerField()
    name = models.CharField(max_length=200)
    description = models.TextField()

    def __str__(self):
        return f'{self.index} - {self.name} - {self.description}'

    class Meta:
        verbose_name_plural = 'Steps'


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
