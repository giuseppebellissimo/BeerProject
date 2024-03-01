from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Category)
admin.site.register(Ingredient)
admin.site.register(Recipe)
admin.site.register(Inventory)
admin.site.register(Step)
admin.site.register(IngredientRecipe)
admin.site.register(InventoryIngredient)
