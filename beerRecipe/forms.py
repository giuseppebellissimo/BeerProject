from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from beerRecipe.models import Recipe, Step, Inventory


class NewUserForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super(NewUserForm, self).save(commit=False)
        user.email = self.cleaned_data['email']

        if commit:
            user.save()

        return user


class AddRecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ['name', 'litre', 'ebc', 'ibu']


class AddStepForm(forms.ModelForm):
    class Meta:
        model = Step
        fields = ['index', 'name', 'description']


class AddInventoryForm(forms.ModelForm):
    class Meta:
        model = Inventory
        fields = ['name']
