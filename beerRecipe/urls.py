from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_user, name='login_user'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.logout_user, name='logout_user'),
    path('home/', views.home, name='home'),
    path('add-recipe/', views.add_recipe, name='add-recipe'),
    path('add-ingredient-recipe/<int:recipe_id>', views.add_ingredient_to_recipe,
         name='add-ingredient-recipe'),
    path('add-step-recipe/<int:recipe_id>', views.add_step_to_recipe,
         name='add-step-recipe'),
    path('add-inventory', views.add_inventory, name='add-inventory'),
    path('list-ingredient/<int:inventory_id>', views.list_ingredient, name='list_ingredient'),
    path('manage-ingredient-inventory/<int:inventory_id>/<int:ingredient_id>/', views.manage_ingredients_inventory,
         name='manage-ingredient-inventory'),
    path('manage-ingredient-inventory/<int:inventory_id>/', views.manage_ingredients_inventory,
         name='manage-ingredient-inventory'),
    path('remove-ingredient-inventory/<int:ingredient_id>', views.remove_ingredient_from_inventory,
         name='remove-ingredient-inventory'),
]
