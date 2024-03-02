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
]
