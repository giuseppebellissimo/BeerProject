from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from .forms import NewUserForm, AddRecipeForm
from .models import Recipe


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
    return render(request, 'beerRecipe/home.html', {'recipes': recipes})


@login_required
def add_recipe(request):
    if request.method == 'POST':
        recipe_form = AddRecipeForm(request.POST)
        if recipe_form.is_valid():
            recipe = recipe_form.save(commit=False)
            recipe.id_user = request.user
            recipe.save()
            return redirect('home')
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
            return redirect('home')
        else:
            return render(request, 'beerRecipe/addRecipe.html', {'error': recipe_form.errors})
    else:
        recipe_form = AddRecipeForm(instance=recipe)
        return render(request, 'beerRecipe/addRecipe.html', {'recipe_form': recipe_form})


def add_step(request, recipe_id):
    recipe = Recipe.objects.get(id=recipe_id)
