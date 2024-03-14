import yaml
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.http import JsonResponse, HttpResponseServerError, HttpResponseNotAllowed
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
    for ingredient in ingredients:
        property_string = ingredient.id_ingredient.property
        if property_string:
            property_dict = yaml.safe_load(property_string)
            print(f"Proprietà per {ingredient.id_ingredient.name}: {property_dict}")
            ingredient.id_ingredient.properties_dict = property_dict

    context = {
        'ingredients': ingredients,
        'inventories': inventories,
    }
    return render(request, 'beerRecipe/listIngredient.html', context)


def add_ingredient_to_inventory(request, inventory_id):
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

        inventories = Inventory.objects.get(id=inventory_id)
        response = {'inventory_ingredient_form': inventory_ingredient_form, 'property_formset': property_formset,
                    'inventories': inventories}
        return render(request, 'beerRecipe/addIngredient2Inventory.html', response)

    elif request.method == 'POST':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':

            name_ingredient = request.POST.get('name_ingredient')
            name_category = request.POST.get('name_category')
            name_new_category = request.POST.get('name_new_category')
            quantity = request.POST.get('quantity')
            measurement_unit = request.POST.get('measurement_unit')
            expiry_date = request.POST.get('expiry_date')

            if name_category and name_new_category:
                return JsonResponse(
                    {'error': "Both 'Name Category' and 'New Category Name' cannot be filled at the same time."},
                    status=400)

            properties = get_data_formset(request)

            if properties is None:
                return JsonResponse({'error': 'Invalid property data'}, status=400)
            properties_yaml = yaml.dump(properties)

            try:
                if name_new_category:
                    category, created = Category.objects.get_or_create(name=name_new_category)
                else:
                    category = Category.objects.get(id=name_category)

                ingredient = Ingredient.objects.create(name=name_ingredient, id_category=category,
                                                       property=properties_yaml)

                inventory = Inventory.objects.get(id=inventory_id)
                InventoryIngredient.objects.create(
                    quantity=quantity,
                    measurement_unit=measurement_unit,
                    expiry_date=expiry_date,
                    id_inventory=inventory,
                    id_ingredient=ingredient
                )
                return JsonResponse({'success': 'Ingredient added successfully'})

            except Exception as e:
                print(e)
                return JsonResponse({'error': 'Internal server error'}, status=500)
        else:
            return JsonResponse({'error': 'Invalid AJAX request'}, status=400)
    else:
        return HttpResponseNotAllowed(['GET', 'POST'])


def get_data_formset(request):
    properties = {}
    i = 0

    while True:
        name_key = f'property-{i}-name'
        value_key = f'property-{i}-value'

        if name_key in request.POST and value_key in request.POST:
            name = request.POST[name_key]
            value = request.POST[value_key]

            if name and value:
                properties[name] = value
        else:
            break

        i += 1

    if properties:
        return properties
    else:
        return HttpResponseServerError('Property does not exist')
