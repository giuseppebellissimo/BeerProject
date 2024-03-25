import yaml
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.http import JsonResponse, HttpResponseNotAllowed, HttpResponseNotFound
from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist

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


@login_required
def logout_user(request):
    logout(request)
    return redirect('login_user')


@login_required
def home(request):
    recipes = Recipe.objects.filter(id_user=request.user)
    inventories = Inventory.objects.filter(id_user=request.user)
    return render(request, 'beerRecipe/home.html', {'recipes': recipes, 'inventories': inventories})


@login_required
def add_recipe(request):
    if request.method == 'GET':
        recipe_form = RecipeForm()
        context = {
            'recipe_form': recipe_form,
        }
        return render(request, 'beerRecipe/addRecipe.html', context)
    elif request.method == 'POST':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            recipe_form = RecipeForm(request.POST)

            if recipe_form.is_valid():
                recipe = recipe_form.save(commit=False)
                recipe.id_user = request.user
                recipe.save()
                return JsonResponse({'success': 'Recipe saved successfully', 'recipe_id': recipe.id})
            else:
                return JsonResponse({'error': recipe_form.errors}, status=400)
        else:
            return JsonResponse({'error': 'Invalid AJAX request'}, status=500)
    else:
        return HttpResponseNotAllowed(['GET', 'POST'])


@login_required
def add_ingredient_to_recipe(request, recipe_id):
    if request.method == 'GET':
        ingredient_form = IngredientRecipeForm()
        initial_property_data = [{'name': 'AA', 'value': ''},
                                 {'name': 'EBC', 'value': ''},
                                 {'name': 'Format', 'value': ''},
                                 ]
        property_ingredient_recipe = property_ingredient_formset(initial=initial_property_data, prefix='property')
        for i, form in enumerate(property_ingredient_recipe.forms):
            if i < 3:
                form.fields['name'].disabled = True

        context = {
            'property_ingredient_recipe': property_ingredient_recipe,
            'ingredient_form': ingredient_form,
            'recipe_id': recipe_id
        }
        return render(request, 'beerRecipe/addIngredientRecipe.html', context)
    elif request.method == 'POST':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            name_ingredient = request.POST.get('name_ingredient')
            name_category = request.POST.get('name_category')
            name_new_category = request.POST.get('name_new_category')
            quantity = request.POST.get('quantity')
            measurement_unit = request.POST.get('measurement_unit')
            properties = get_data_formset(request)
            properties_yaml = yaml.dump(properties)

            if name_category and name_new_category:
                return JsonResponse(
                    {'error': "Both 'Name Category' and 'New Category Name' cannot be filled at the same time."},
                    status=400)
            if name_new_category:
                category, created = Category.objects.get_or_create(name=name_new_category)
            else:
                category = Category.objects.get(id=name_category)

            ingredient = Ingredient.objects.create(
                name=name_ingredient,
                id_category=category,
                property=properties_yaml,
            )
            recipe = Recipe.objects.get(id=recipe_id)
            IngredientRecipe.objects.create(
                id_recipe=recipe,
                id_ingredient=ingredient,
                quantity=quantity,
                measurement_unit=measurement_unit,
            )
            return JsonResponse({'success': 'Ingredient added successfully'})
        else:
            return JsonResponse({'error': 'Invalid AJAX request'}, status=400)
    else:
        return HttpResponseNotAllowed(['GET', 'POST'])


@login_required
def add_step_to_recipe(request, recipe_id):
    if request.method == 'GET':
        step_form = step_formset(prefix='step')
        context = {
            'step_form': step_form,
            'recipe_id': recipe_id
        }
        return render(request, 'beerRecipe/addStepRecipe.html', context)
    elif request.method == 'POST':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            total_forms = int(request.POST.get('step-TOTAL_FORMS'))
            recipe = Recipe.objects.get(id=recipe_id)
            for i in range(total_forms):
                index = request.POST.get(f'step-{i}-index')
                name = request.POST.get(f'step-{i}-name')
                description = request.POST.get(f'step-{i}-description')
                Step.objects.create(
                    index=index,
                    name=name,
                    description=description,
                    id_recipe=recipe,
                )
            return JsonResponse({'success': 'Step added successfully'})
        else:
            return JsonResponse({'error': 'Invalid AJAX request'}, status=400)
    else:
        return HttpResponseNotAllowed(['GET', 'POST'])


@login_required
def view_recipes(request, recipe_id):
    recipe = Recipe.objects.get(id=recipe_id)
    ingredients = IngredientRecipe.objects.filter(id_recipe=recipe_id)
    steps = Step.objects.filter(id_recipe=recipe_id)
    for ingredient in ingredients:
        property_string = ingredient.id_ingredient.property
        if property_string:
            property_dict = yaml.safe_load(property_string)
            ingredient.id_ingredient.properties_dict = property_dict
    context = {
        'recipe': recipe,
        'ingredients': ingredients,
        'steps': steps,
    }
    return render(request, 'beerRecipe/viewRecipe.html', context)


@login_required
def remove_ingredient_form_recipe(request, ingredient_id):
    try:
        ingredient = Ingredient.objects.get(id=ingredient_id)
        ingredient_recipe = IngredientRecipe.objects.get(id_ingredient=ingredient_id)
        recipe = ingredient_recipe.id_recipe.id
    except ObjectDoesNotExist:
        return HttpResponseNotFound()
    ingredient.delete()
    ingredient_recipe.delete()
    return redirect('view-recipe', recipe)


@login_required
def remove_step_from_recipe(request, step_id):
    try:
        step = Step.objects.get(id=step_id)
        recipe = step.id_recipe.id
    except ObjectDoesNotExist:
        return HttpResponseNotFound()
    step.delete()
    return redirect('view-recipe', recipe)


@login_required
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


@login_required
def list_ingredient(request, inventory_id):
    inventories = Inventory.objects.get(id=inventory_id)
    ingredients = InventoryIngredient.objects.filter(id_inventory=inventory_id)
    categories = Category.objects.all()
    for ingredient in ingredients:
        property_string = ingredient.id_ingredient.property
        if property_string:
            property_dict = yaml.safe_load(property_string)
            ingredient.id_ingredient.properties_dict = property_dict

    context = {
        'ingredients': ingredients,
        'inventories': inventories,
        'categories': categories,
    }
    return render(request, 'beerRecipe/listIngredient.html', context)


@login_required
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

    return properties


@login_required
def remove_ingredient_from_inventory(request, ingredient_id):
    try:
        ingredient = Ingredient.objects.get(id=ingredient_id)
        inventory_ingredient = InventoryIngredient.objects.get(id_ingredient=ingredient_id)
        inventory = inventory_ingredient.id_inventory.id
    except ObjectDoesNotExist:
        return HttpResponseNotFound()
    ingredient.delete()
    inventory_ingredient.delete()
    return redirect('list_ingredient', inventory)


@login_required
def manage_ingredients_inventory(request, inventory_id, ingredient_id=None):
    try:
        inventory = Inventory.objects.get(id=inventory_id)
    except ObjectDoesNotExist:
        return HttpResponseNotFound()

    if ingredient_id:
        try:
            ingredient = InventoryIngredient.objects.get(id_ingredient=ingredient_id)
            initial_data = {
                'name_ingredient': ingredient.id_ingredient.name,
                'name_category': ingredient.id_ingredient.id_category,
                'quantity': ingredient.quantity,
                'measurement_unit': ingredient.measurement_unit,
                'expiry_date': ingredient.expiry_date,
            }

            property_data = yaml.safe_load(
                ingredient.id_ingredient.property) if ingredient.id_ingredient.property else []
            initial_property_data = [{'name': key, 'value': value} for key, value in property_data.items()]

            property_formset = property_ingredient_formset(initial=initial_property_data, prefix='property')
        except ObjectDoesNotExist:
            return HttpResponseNotFound("Ingredient not found")
    else:
        ingredient = None
        initial_data = {}

        initial_property_data = [{'name': 'AA', 'value': ''},
                                 {'name': 'EBC', 'value': ''},
                                 {'name': 'Format', 'value': ''},
                                 ]
        property_formset = property_ingredient_formset(initial=initial_property_data, prefix='property')
        for i, form in enumerate(property_formset.forms):
            if i < 3:
                form.fields['name'].disabled = True

    if request.method == 'GET':
        inventory_ingredient_form = InventoryIngredientForm(initial=initial_data)
        context = {
            'inventory_ingredient_form': inventory_ingredient_form,
            'property_formset': property_formset,
            'inventory': inventory,
            'ingredient': ingredient,
        }
        return render(request, 'beerRecipe/manageIngredientInventory.html', context)

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
            properties_yaml = yaml.dump(properties)

            try:
                if name_new_category:
                    category, created = Category.objects.get_or_create(name=name_new_category)
                else:
                    category = Category.objects.get(id=name_category)

                ingredient, created = Ingredient.objects.update_or_create(id=ingredient_id,
                                                                          defaults={
                                                                              'name': name_ingredient,
                                                                              'id_category': category,
                                                                              'property': properties_yaml,
                                                                          })
                InventoryIngredient.objects.update_or_create(
                    id_inventory=inventory,
                    id_ingredient=ingredient,
                    defaults={
                        'quantity': quantity,
                        'measurement_unit': measurement_unit,
                        'expiry_date': expiry_date,
                    })
                return JsonResponse({'success': 'Ingredient added successfully'})
            except Exception as e:
                return JsonResponse({'error': e}, status=500)
        else:
            return JsonResponse({'error': 'Invalid AJAX request'}, status=400)
    else:
        return HttpResponseNotAllowed(['GET', 'POST'])
