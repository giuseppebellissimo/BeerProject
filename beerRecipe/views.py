from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm


# Create your views here.
def index(request):
    return render(request, 'beerRecipe/root.html')


@login_required
def login_user(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('root')

        else:
            return render(request, 'beerRecipe/login.html', {'form': form})

    else:
        form = AuthenticationForm()

    return render(request, 'beerRecipe/login.html', {'form': form})


def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)

        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('root')
        else:
            return render(request, "beerRecipe/signup.html", {'form': form})

    else:
        form = UserCreationForm()

    return render(request, "beerRecipe/signup.html", {'form': form})
