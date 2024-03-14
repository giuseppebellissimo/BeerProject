from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_user, name='login_user'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.logout_user, name='logout_user'),
    path('home/', views.home, name='home'),
    path('recipes/', views.add_recipe, name='recipes'),
    path('delete-recipe/<int:recipe_id>', views.delete_recipe, name='delete_recipe'),
    path('edit-recipe/<int:recipe_id>', views.edit_recipe, name='edit_recipe'),
    path('steps/<int:recipe_id>', views.add_step, name='steps'),
    path('add-inventory', views.add_inventory, name='add-inventory'),
    path('list-ingredient/<int:inventory_id>', views.list_ingredient, name='list_ingredient'),
    path('add-ingredient-inventory/<int:inventory_id>', views.add_ingredient_to_inventory,
         name='add-ingredient-inventory'),
]
