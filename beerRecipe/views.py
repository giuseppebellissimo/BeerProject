import yaml
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.db import IntegrityError
from django.http import JsonResponse, HttpResponseNotAllowed, HttpResponseNotFound
from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist, ValidationError

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
    default_inventory = inventories.filter(is_default=True).first()
    return render(request, 'beerRecipe/home.html',
                  {'recipes': recipes, 'inventories': inventories, 'default_inventory': default_inventory})


@login_required
def set_default_inventory(request, inventory_id):
    try:
        Inventory.objects.filter(id_user=request.user).update(is_default=False)
        default_inventory = Inventory.objects.get(id=inventory_id, id_user=request.user)
        default_inventory.is_default = True
        default_inventory.save()
    except Inventory.DoesNotExist:
        return HttpResponseNotFound("Inventory does not exist")
    return redirect('home')


@login_required
def equivalent_ingredients(request):
    inventory = Inventory.objects.filter(id_user=request.user)
    ingredients = Ingredient.objects.filter(inventory__in=inventory)
    equivalent_classes = EquivalentIngredients.objects.filter(user=request.user)
    context = {
        'ingredients': ingredients,
        'equivalent_classes': equivalent_classes
    }
    return render(request, 'beerRecipe/equivalentIngredients.html', context)


@login_required
def add_equivalence_classes_of_ingredients(request):
    if request.method == 'GET':
        form = EquivalenceClassesForm()
        context = {'form': form}
        return render(request, 'beerRecipe/addEquivalenceClasses.html', context)
    elif request.method == 'POST':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            name = request.POST.get('name')
            description = request.POST.get('description')
            try:
                equivalent = EquivalentIngredients.objects.create(name=name, description=description)
                equivalent.save()
                equivalent.user.add(request.user)
            except IntegrityError:
                return JsonResponse({'error': 'Integrity error while adding an equivalent ingredient'}, status=400)
            except ValidationError as e:
                return JsonResponse({'error': f'Validation error: {e.message}'}, status=400)
            except Exception as e:
                return JsonResponse({'error': f'Unexpected error: {str(e)}'}, status=500)
            return JsonResponse({'success': 'Recipe saved successfully'})
        else:
            return JsonResponse({'error': 'Invalid AJAX request'}, status=500)
    else:
        return HttpResponseNotAllowed(['GET', 'POST'])


@login_required
def update_equivalence_classes_of_ingredients(request):
    if request.method == 'POST':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            ingredient_id = request.POST.get('ingredient_id')
            equivalent_class_id = request.POST.get('equivalent_class_id')

            try:
                ingredient = Ingredient.objects.get(id=ingredient_id)
                equivalent_class = EquivalentIngredients.objects.get(id=equivalent_class_id)
                equivalent_class.ingredients.add(ingredient)
                equivalent_class.save()
                return JsonResponse({'success': 'Ingredient added successfully'})
            except Ingredient.DoesNotExist:
                return JsonResponse({'error': 'Ingredient does not exist'}, status=404)
            except EquivalentIngredients.DoesNotExist:
                return JsonResponse({'error': 'Equivalent class does not exist'}, status=404)
            except IntegrityError as e:
                return JsonResponse({'error': str(e)}, status=400)
    return HttpResponseNotAllowed(['POST'])


@login_required
def add_recipe(request, recipe_id=None):
    hide_button = request.GET.get('hide_back_button', 'true') == 'true'
    if recipe_id:
        try:
            recipe = Recipe.objects.get(id=recipe_id)
            initial_data = {
                'name': recipe.name,
                'litre': recipe.litre,
                'ebc': recipe.ebc,
                'ibu': recipe.ibu,
                'id_user': recipe.id_user
            }
        except ObjectDoesNotExist:
            return HttpResponseNotFound("Recipe does not exist")
    else:
        initial_data = {}
        recipe = None

    if request.method == 'GET':
        recipe_form = RecipeForm(initial=initial_data)
        context = {
            'recipe_form': recipe_form,
            'recipe': recipe,
            'hide_button': hide_button,
        }
        return render(request, 'beerRecipe/addRecipe.html', context)
    elif request.method == 'POST':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            name = request.POST.get('name')
            litre = request.POST.get('litre')
            ebc = request.POST.get('ebc')
            ibu = request.POST.get('ibu')
            recipe, created = Recipe.objects.update_or_create(
                id=recipe_id,
                defaults={
                    'name': name,
                    'litre': litre,
                    'ebc': ebc,
                    'ibu': ibu,
                    'id_user': request.user
                }
            )
            return JsonResponse({'success': 'Recipe saved successfully', 'recipe_id': recipe.id})
        else:
            return JsonResponse({'error': 'Invalid AJAX request'}, status=500)
    else:
        return HttpResponseNotAllowed(['GET', 'POST'])


@login_required
def check_missing_ingredients_from_recipe(request):
    recipe_id = request.GET.get('recipe_id')
    inventory = Inventory.objects.filter(id_user=request.user)
    default_inventory = inventory.filter(is_default=True).first()
    if not default_inventory:
        return JsonResponse({'error': 'Default inventory not found'}, status=404)

    ingredients_recipe = IngredientRecipe.objects.filter(id_recipe=recipe_id).select_related('id_ingredient')
    name_recipe = Recipe.objects.get(id=recipe_id).name
    missing_ingredients = []

    if not ingredients_recipe:
        response = {
            'name_recipe': name_recipe,
            'has_no_ingredients': True,
        }
        return JsonResponse(response)

    for ingredient in ingredients_recipe:
        inventory_ingredient = InventoryIngredient.objects.get(id_inventory=default_inventory.id,
                                                               id_ingredient=ingredient.id_ingredient)
        if inventory_ingredient.quantity < ingredient.quantity:
            missing_quantity = inventory_ingredient.quantity - ingredient.quantity
            missing_ingredients.append({
                'name_ingredient': ingredient.id_ingredient.name,
                'recipe_quantity': ingredient.quantity,
                'available_quantity': inventory_ingredient.quantity,
                'missing_quantity': abs(missing_quantity),
                'measurement_unit': ingredient.measurement_unit
            })

    return JsonResponse({'missing_ingredients': missing_ingredients, 'name_recipe': name_recipe})


@login_required
def add_ingredient_to_recipe(request, recipe_id, ingredient_id=None):
    try:
        recipe = Recipe.objects.get(id=recipe_id)
    except ObjectDoesNotExist:
        return HttpResponseNotFound()
    hide_button = request.GET.get('hide_back_button', 'true') == 'true'
    hide_navbar = request.GET.get('hide_navbar_ingredient', 'true') == 'true'
    core_only = request.GET.get('core_only', 'false') == 'true'
    inventory = Inventory.objects.filter(id_user=request.user)
    default_inventory = inventory.filter(is_default=True).first()

    if ingredient_id:
        try:
            ingredient = IngredientRecipe.objects.get(id_ingredient=ingredient_id)
            initial_data = {
                'name_ingredient': ingredient.id_ingredient.name,
                'name_category': ingredient.id_ingredient.id_category,
                'comment': ingredient.id_ingredient.comment,
                'producer': ingredient.id_ingredient.producer,
                'quantity': ingredient.quantity,
                'measurement_unit': ingredient.measurement_unit,
            }
            property_data = yaml.safe_load(
                ingredient.id_ingredient.property) if ingredient.id_ingredient.property else []
            initial_property_data = [{'name': key, 'value': value} for key, value in property_data.items()]
            property_ingredient_recipe = property_ingredient_formset(initial=initial_property_data, prefix='property')
        except ObjectDoesNotExist:
            return HttpResponseNotFound('Ingredient not found')
    else:
        ingredient = None
        initial_data = {}
        initial_property_data = [{'name': 'AA', 'value': ''},
                                 {'name': 'EBC', 'value': ''},
                                 {'name': 'Format', 'value': ''},
                                 ]
        property_ingredient_recipe = property_ingredient_formset(initial=initial_property_data, prefix='property')
        for i, form in enumerate(property_ingredient_recipe.forms):
            if i < 3:
                form.fields['name'].disabled = True

    if request.method == 'GET':
        ingredient_form = IngredientRecipeForm(initial=initial_data)
        context = {
            'property_ingredient_recipe': property_ingredient_recipe,
            'ingredient_form': ingredient_form,
            'ingredient': ingredient,
            'recipe': recipe,
            'default_inventory': default_inventory,
            'hide_navbar': hide_navbar,
            'hide_button': hide_button
        }
        if core_only:
            template_name = 'beerRecipe/coreIngredientRecipe.html'
        else:
            template_name = 'beerRecipe/addIngredientRecipe.html'
        return render(request, template_name, context)

    elif request.method == 'POST':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            name_ingredient = request.POST.get('name_ingredient')
            name_category = request.POST.get('name_category')
            name_new_category = request.POST.get('name_new_category')
            quantity = request.POST.get('quantity')
            measurement_unit = request.POST.get('measurement_unit')
            comment = request.POST.get('comment')
            producer = request.POST.get('producer')
            ingredient_selected = request.POST.get('ingredient_selected')

            total_forms = int(request.POST.get('total_forms'))
            properties = get_data_formset(request, total_forms)
            properties_yaml = yaml.dump(properties)

            original_unit = measurement_unit
            quantity, measurement_unit = convert_measurement(request, quantity, measurement_unit)

            if name_category and name_new_category:
                return JsonResponse(
                    {'error': "Both 'Name Category' and 'New Category Name' cannot be filled at the same time."},
                    status=400)
            if name_new_category:
                category, created = Category.objects.get_or_create(name=name_new_category)
            else:
                category = Category.objects.get(id=name_category)

            if ingredient_selected:
                ingredient = Ingredient.objects.get(id=ingredient_selected)
            else:
                ingredient, created = Ingredient.objects.update_or_create(
                    id=ingredient_id,
                    defaults={
                        'name': name_ingredient,
                        'id_category': category,
                        'property': properties_yaml,
                        'comment': comment,
                        'producer': producer
                    })

            IngredientRecipe.objects.update_or_create(
                id_recipe=recipe,
                id_ingredient=ingredient,
                defaults={
                    'quantity': quantity,
                    'measurement_unit': measurement_unit,
                    'original_unit': original_unit
                })

            if ingredient_id is None and ingredient_selected == '':
                InventoryIngredient.objects.update_or_create(
                    id_inventory=default_inventory,
                    id_ingredient=ingredient,
                    defaults={
                        'quantity': 0,
                        'measurement_unit': measurement_unit,
                        'original_unit': original_unit,
                        'expiry_date': None
                    })
            return JsonResponse({'success': 'Ingredient added successfully'})
        else:
            return JsonResponse({'error': 'Invalid AJAX request'}, status=400)
    else:
        return HttpResponseNotAllowed(['GET', 'POST'])


@login_required
def convert_measurement(request, quantity, measurement_unit):
    conversion = {
        'Kg': lambda x: x * 1000,
        'hg': lambda x: x * 100,
        'gr': lambda x: x,
        'mg': lambda x: x / 1000,
        'L': lambda x: x,
        'cl': lambda x: x / 100,
        'ml': lambda x: x / 1000,
        'DRY_YEASTS_11': lambda x: x * 11,
        'DRY_YEASTS_100': lambda x: x * 100,
        'DRY_YEASTS_500': lambda x: x * 500,
    }
    final_unit = {
        'Kg': 'gr', 'hg': 'gr', 'mg': 'gr', 'gr': 'gr', 'DRY_YEASTS_11': 'gr', 'DRY_YEASTS_100': 'gr',
        'DRY_YEASTS_500': 'gr', 'L': 'L', 'cl': 'L', 'ml': 'L'
    }
    if measurement_unit in conversion:
        converted_quantity = conversion[measurement_unit](float(quantity))
        new_measurement_unit = final_unit[measurement_unit]
        return converted_quantity, new_measurement_unit
    return float(quantity), measurement_unit


def inverse_convert_measurement(request, quantity, measurement_unit):
    conversion = {
        'Kg': lambda x: x / 1000,
        'hg': lambda x: x / 100,
        'gr': lambda x: x,
        'mg': lambda x: x * 1000,
        'L': lambda x: x,
        'cl': lambda x: x * 100,
        'ml': lambda x: x * 1000,
        'DRY_YEASTS_11': lambda x: x / 11,
        'DRY_YEASTS_100': lambda x: x / 100,
        'DRY_YEASTS_500': lambda x: x / 500,
    }
    if measurement_unit in conversion:
        converted_quantity = conversion[measurement_unit](float(quantity))
        return converted_quantity
    return float(quantity)


@login_required
def load_ingredients_from_inventory(request):
    inventory = Inventory.objects.filter(id_user=request.user)
    default_inventory = inventory.filter(is_default=True).first()

    if default_inventory:
        inventory_ingredients = InventoryIngredient.objects.filter(id_inventory=default_inventory).select_related(
            'id_ingredient')
        ingredients = [{
            'id': inv_ingredient.id_ingredient.id,
            'name': inv_ingredient.id_ingredient.name,
            'quantity': inv_ingredient.quantity,
            'measurement_unit': inv_ingredient.measurement_unit
        } for inv_ingredient in inventory_ingredients]
    else:
        ingredients = []
    return JsonResponse(list(ingredients), safe=False)


@login_required
def add_selected_ingredients(request):
    ingredient_id = request.GET.get('ingredient_id')
    try:
        ingredient = InventoryIngredient.objects.get(id_ingredient=ingredient_id)
    except ObjectDoesNotExist:
        return JsonResponse({'error': 'Ingredient not found'}, status=400)

    property_data = yaml.safe_load(
        ingredient.id_ingredient.property) if ingredient.id_ingredient.property else []
    properties_list = [{'name': key, 'value': value} for key, value in property_data.items()]
    ingredient_data = {
        'name_ingredient': ingredient.id_ingredient.name,
        'name_category': ingredient.id_ingredient.id_category.id,
        'quantity': ingredient.quantity,
        'measurement_unit': ingredient.original_unit,
        'properties': properties_list
    }
    return JsonResponse(ingredient_data)


@login_required
def add_step_to_recipe(request, recipe_id, step_id=None):
    try:
        recipe = Recipe.objects.get(id=recipe_id)
    except ObjectDoesNotExist:
        return HttpResponseNotFound()
    hide_button = request.GET.get('hide_back_button', 'true') == 'true'
    hide_navbar = request.GET.get('hide_navbar_ingredient', 'true') == 'true'
    core_only = request.GET.get('core_only', 'false') == 'true'
    if step_id:
        try:
            step = Step.objects.get(id=step_id)
            initial_data = [{'index': step.index, 'name': step.name, 'description': step.description}
                            for step in Step.objects.filter(id_recipe=recipe)]
        except ObjectDoesNotExist:
            return HttpResponseNotFound('Step not found')
    else:
        initial_data = []
        step = None

    if request.method == 'GET':
        step_form = step_formset(prefix='step', initial=initial_data)
        context = {
            'step_form': step_form,
            'recipe_id': recipe_id,
            'step': step,
            'recipe': recipe,
            'hide_navbar': hide_navbar,
            'hide_button': hide_button
        }
        if core_only:
            template_name = 'beerRecipe/coreStepRecipe.html'
        else:
            template_name = 'beerRecipe/addStepRecipe.html'
        return render(request, template_name, context)

    elif request.method == 'POST':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            total_forms = int(request.POST.get('step-TOTAL_FORMS'))

            for i in range(total_forms):
                index = request.POST.get(f'step-{i}-index')
                name = request.POST.get(f'step-{i}-name')
                description = request.POST.get(f'step-{i}-description')
                Step.objects.update_or_create(
                    id=step_id,
                    defaults={
                        'index': index,
                        'name': name,
                        'description': description,
                        'id_recipe': recipe
                    })
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
        measurement_unit = ingredient.original_unit
        quantity = ingredient.quantity
        converted_quantity = inverse_convert_measurement(request, quantity, measurement_unit)
        ingredient.display_quantity = converted_quantity

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
        ingredient_recipe = IngredientRecipe.objects.get(id_ingredient=ingredient_id)
        recipe = ingredient_recipe.id_recipe.id
    except ObjectDoesNotExist:
        return HttpResponseNotFound()

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
def remove_recipe(request, recipe_id):
    try:
        recipe = Recipe.objects.get(id=recipe_id)
    except ObjectDoesNotExist:
        return HttpResponseNotFound("Recipe does not exist")

    ingredient_recipes = IngredientRecipe.objects.filter(id_recipe=recipe_id)
    for ingredient_recipe in ingredient_recipes:
        ingredient = ingredient_recipe.id_ingredient
        ingredient_recipe.delete()
        if not (IngredientRecipe.objects.filter(id_ingredient=ingredient).exists() or
                InventoryIngredient.objects.filter(id_ingredient=ingredient).exists()):
            ingredient.delete()

    for step in Step.objects.filter(id_recipe=recipe_id):
        step.delete()

    recipe.delete()
    return redirect('home')


@login_required
def add_inventory(request, inventory_id=None):
    if inventory_id:
        try:
            inventory = Inventory.objects.get(id=inventory_id)
            initial_data = {
                'name': inventory.name,
            }
        except ObjectDoesNotExist:
            return HttpResponseNotFound("Inventory does not exist")
    else:
        initial_data = {}
        inventory = None

    if request.method == 'GET':
        inventory_form = AddInventoryForm(initial=initial_data)
        context = {
            'inventory_form': inventory_form,
            'inventory': inventory
        }
        return render(request, 'beerRecipe/addInventory.html', context)
    if request.method == 'POST':
        inventory_form = AddInventoryForm(request.POST, instance=inventory)
        if inventory_form.is_valid():
            new_inventory = inventory_form.save(commit=False)
            if not inventory_id:
                new_inventory.save()
                new_inventory.id_user.set([request.user])
            else:
                new_inventory.save()
            return redirect('home')
        else:
            return render(request, 'beerRecipe/addInventory.html', {'error': inventory_form.errors})


@login_required
def remove_inventory(request, inventory_id):
    try:
        inventory = Inventory.objects.get(id=inventory_id)
    except ObjectDoesNotExist:
        return HttpResponseNotFound("Inventory does not exist")

    ingredient_inventories = InventoryIngredient.objects.filter(id_inventory=inventory_id)
    for ingredient_inventory in ingredient_inventories:
        ingredient = ingredient_inventory.id_ingredient
        ingredient_inventory.delete()
        if not (IngredientRecipe.objects.filter(id_ingredient=ingredient).exists() or
                InventoryIngredient.objects.filter(id_ingredient=ingredient).exists()):
            ingredient.delete()

    inventory.delete()
    return redirect('home')


@login_required
def list_ingredient(request, inventory_id):
    inventories = Inventory.objects.get(id=inventory_id)
    ingredients = InventoryIngredient.objects.filter(id_inventory=inventory_id)
    categories = Category.objects.all()

    for ingredient in ingredients:
        measurement_unit = ingredient.original_unit
        quantity = ingredient.quantity
        converted_quantity = inverse_convert_measurement(request, quantity, measurement_unit)
        ingredient.display_quantity = converted_quantity

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
def get_data_formset(request, total_forms):
    properties = {}

    for index in range(total_forms):
        name_key = f'property-{index}-name'
        value_key = f'property-{index}-value'

        if name_key in request.POST and value_key in request.POST:
            name = request.POST[name_key]
            value = request.POST[value_key]

            if name and value:
                properties[name] = value

    return properties


@login_required
def remove_ingredient_from_inventory(request, ingredient_id):
    try:
        ingredient = Ingredient.objects.get(id=ingredient_id)
        inventory_ingredient = InventoryIngredient.objects.get(id_ingredient=ingredient_id)
        inventory = Inventory.objects.get(id=inventory_ingredient.id_inventory.id)
    except ObjectDoesNotExist:
        return HttpResponseNotFound()
    ingredient.delete()
    inventory_ingredient.delete()
    inventory.save()
    return redirect('list_ingredient', inventory.id)


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
                'comment': ingredient.id_ingredient.comment,
                'producer': ingredient.id_ingredient.producer,
                'quantity': ingredient.quantity,
                'measurement_unit': ingredient.measurement_unit,
                'expiry_date': ingredient.expiry_date
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
            expiry_date = request.POST.get('expiry_date') or None
            comment = request.POST.get('comment')
            producer = request.POST.get('producer')

            total_forms = int(request.POST.get('total_forms'))
            properties = get_data_formset(request, total_forms)
            properties_yaml = yaml.dump(properties)

            if expiry_date == '':
                expiry_date = None

            original_unit = measurement_unit
            quantity, measurement_unit = convert_measurement(request, quantity, measurement_unit)

            if name_category and name_new_category:
                return JsonResponse(
                    {'error': "Both 'Name Category' and 'New Category Name' cannot be filled at the same time."},
                    status=400)

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
                                                                              'comment': comment,
                                                                              'producer': producer,
                                                                          })
                InventoryIngredient.objects.update_or_create(
                    id_inventory=inventory,
                    id_ingredient=ingredient,
                    defaults={
                        'quantity': quantity,
                        'measurement_unit': measurement_unit,
                        'expiry_date': expiry_date,
                        'original_unit': original_unit
                    })
                inventory.save()
                return JsonResponse({'success': 'Ingredient added successfully'})
            except Exception as e:
                return JsonResponse({'error': e}, status=500)
        else:
            return JsonResponse({'error': 'Invalid AJAX request'}, status=400)
    else:
        return HttpResponseNotAllowed(['GET', 'POST'])
