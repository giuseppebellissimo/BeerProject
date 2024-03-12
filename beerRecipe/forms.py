from django import forms
from django.contrib.auth.forms import UserCreationForm
from crispy_forms.bootstrap import Div, InlineCheckboxes
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row
from django.forms import formset_factory

from beerRecipe.models import *


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


class InventoryIngredientForm(forms.ModelForm):
    name_ingredient = forms.CharField(max_length=100)
    category_choices = forms.MultipleChoiceField(choices=CATEGORY_CHOICES, required=False,
                                                 widget=forms.CheckboxSelectMultiple)
    name_category = forms.ModelChoiceField(queryset=Category.objects.all(), empty_label='---')
    name_new_category = forms.CharField(max_length=100)

    class Meta:
        model = InventoryIngredient
        fields = '__all__'
        exclude = ('id_ingredient', 'id_inventory')

        widgets = {
            'expiry_date': forms.DateInput(attrs={'type': 'date'}, )
        }

        labels = {
            'name_ingredient': 'Name Ingredient',
            'name_category': 'Category',
            'quantity': 'Quantity',
            'measurement_unit': 'Measurement Unit',
            'expiry_date': 'Expiry Date',
            'name_new_category': 'New Category Name',
            'category_choices': 'Category Options',
        }

    def __init__(self, *args, **kwargs):
        super(InventoryIngredientForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = 'POST'

        self.helper.layout = Layout(
            Row(Div('name_ingredient', css_class="col-6"), Div(InlineCheckboxes('category_choices'), css_class="col-6"),
                Div('name_category', css_class="col-6"), Div('name_new_category', css_class="col-6")),
            Row(Div('quantity', css_class="col-3"), Div('measurement_unit', css_class="col-3"),
                Div('expiry_date', css_class="col-3"), )
        )


class PropertyIngredientForm(forms.Form):
    name = forms.CharField(label='Name',
                           widget=forms.TextInput(attrs={'class': 'form-control form-control-sm', }), )
    value = forms.DecimalField(label='Value',
                               widget=forms.NumberInput(attrs={'class': 'form-control form-control-sm'}))


property_ingredient_formset = formset_factory(PropertyIngredientForm, extra=0, min_num=3, can_delete=True)
