from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import render, redirect

from .forms import *
from .models import *


# Create your views here.
def login_user(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            form = AuthenticationForm()
            messages.error(request, f'Invalid username or password')
            return render(request, 'beerRecipe/login.html', {'form': form})
    else:
        form = AuthenticationForm()
        return render(request, 'beerRecipe/login.html', {'form': form})


def signup(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = NewUserForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            if user is not None:
                messages.success(request, f'Welcome {username.title()}, your account has been created successfully!')
                login(request, user)
            return redirect('home')
        else:
            messages.error(request, f'Fill in the form fields correctly')
            return render(request, 'beerRecipe/signup.html', {'error': form.errors})
    else:
        form = NewUserForm()
        return render(request, "beerRecipe/signup.html", {'form': form})


def logout_user(request):
    logout(request)
    return redirect('login_user')


@login_required
def home(request):
    recipes = Recipe.objects.all()
    steps = Step.objects.all()
    inventories = Inventory.objects.filter(id_user=request.user)
    return render(request, 'beerRecipe/home.html', {'recipes': recipes, 'steps': steps, 'inventories': inventories})


def add_recipe(request):
    if request.method == 'POST':
        recipe_form = AddRecipeForm(request.POST)
        if recipe_form.is_valid():
            recipe = recipe_form.save(commit=False)
            recipe.id_user = request.user
            recipe.save()
        else:
            return render(request, 'beerRecipe/addRecipe.html', {'error': recipe_form.errors})
    else:
        recipe_form = AddRecipeForm()
        return render(request, 'beerRecipe/addRecipe.html', {'recipe_form': recipe_form})


def delete_recipe(request, recipe_id):
    recipe = Recipe.objects.get(id=recipe_id)
    recipe.delete()
    return redirect('home')


def edit_recipe(request, recipe_id):
    recipe = Recipe.objects.get(id=recipe_id)

    if request.method == 'POST':
        recipe_form = AddRecipeForm(request.POST, instance=recipe)
        if recipe_form.is_valid():
            recipe = recipe_form.save(commit=False)
            recipe.id_user = request.user
            recipe.save()
            recipe_instance = Recipe.objects.get(id=recipe.id)
            id_recipe = recipe_instance.id
            return redirect('edit_recipe', id_recipe)
        else:
            return render(request, 'beerRecipe/addRecipeId.html', {'error': recipe_form.errors, 'recipe': recipe})
    else:
        recipe_form = AddRecipeForm(instance=recipe)
        return render(request, 'beerRecipe/addRecipeId.html', {'recipe_form': recipe_form, 'recipe': recipe})


def add_step(request, recipe_id):
    recipe = Recipe.objects.get(id=recipe_id)

    if request.method == 'POST':
        step_form = AddStepForm(request.POST)
        if step_form.is_valid():
            step = step_form.save(commit=False)
            step.id_recipe = recipe
            step.save()
            recipe_instance = Recipe.objects.get(id=recipe.id)
            id_recipe = recipe_instance.id
            return redirect('steps', id_recipe)
        else:
            return render(request, 'beerRecipe/addStep.html', {'error': step_form.errors, 'recipe': recipe})
    else:
        step_form = AddStepForm()
        return render(request, 'beerRecipe/addStep.html', {'step_form': step_form, 'recipe': recipe})


def add_inventory(request):
    if request.method == 'POST':
        inventory_form = AddInventoryForm(request.POST)
        if inventory_form.is_valid():
            names = inventory_form.cleaned_data.get('name')
            users = User.objects.filter(id=request.user.id)
            instance = Inventory.objects.create(name=names)
            instance.id_user.set(users)
            return redirect('home')
        else:
            return render(request, 'beerRecipe/addInventory.html', {'error': inventory_form.errors})
    else:
        inventory_form = AddInventoryForm()
        return render(request, 'beerRecipe/addInventory.html', {'inventory_form': inventory_form})


def list_ingredient(request, inventory_id):
    inventories = Inventory.objects.get(id=inventory_id)
    ingredients = InventoryIngredient.objects.filter(id_inventory=inventory_id)
    return render(request, 'beerRecipe/listIngredient.html', {'inventories': inventories, 'ingredients': ingredients})


def add_ingredient_to_inventory(request):
    if request.method == 'GET':
        property_name = [{'name': 'AA', 'value': ''},
                         {'name': 'EBC', 'value': ''},
                         {'name': 'Format', 'value': ''},
                         ]
        inventory_ingredient_form = InventoryIngredientForm()
        inventory_ingredient_form.helper.form_action = 'beerRecipe:add-ingredient-inventory'
        property_formset = property_ingredient_formset(initial=property_name, prefix='property')

        for i, form in enumerate(property_formset.forms):
            if i < 3:
                form.fields['name'].disabled = True

        response = {'inventory_ingredient_form': inventory_ingredient_form, 'property_formset': property_formset}
        return render(request, 'beerRecipe/addIngredient2Inventory.html', response)

    elif request.method == 'POST':
        if request.is_ajax():
            inventory_ingredient_form = InventoryIngredientForm(request.POST)
            property_formset = property_ingredient_formset(request.POST, prefix='property')

            if inventory_ingredient_form.is_valid() and property_formset.is_valid():
                properties = {form.cleaned_data['name']: form.cleaned_data['value'] for form in property_formset}
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'errors': inventory_ingredient_form.errors})

        else:
            raise Http404
