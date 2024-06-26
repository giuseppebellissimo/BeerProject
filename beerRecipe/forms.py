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


class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ['name', 'litre', 'ebc', 'ibu']

        labels = {
            'name': 'Name Recipe',
            'litre': 'Liter',
            'ebc': 'EBC',
            'ibu': 'IBU',
        }

    def __init__(self, *args, **kwargs):
        super(RecipeForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = 'POST'

        self.helper.layout = Layout(
            Row(Div('name', css_class="col-6")),
            Row(Div('litre', css_class="col-3"), Div('ebc', css_class="col-3"),
                Div('ibu', css_class="col-3"), )
        )


class IngredientRecipeForm(forms.ModelForm):
    name_ingredient = forms.CharField(max_length=100)
    category_choices = forms.MultipleChoiceField(choices=CATEGORY_CHOICES, required=False,
                                                 widget=forms.CheckboxSelectMultiple)
    name_category = forms.ModelChoiceField(queryset=Category.objects.all(), empty_label='---')
    name_new_category = forms.CharField(max_length=100)
    measurement_unit = forms.ChoiceField(choices=MEASUREMENT_CHOICES, required=False)
    comment = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control form-control-sm'}), required=False)
    producer = forms.CharField(max_length=100, required=False)

    class Meta:
        model = IngredientRecipe
        fields = '__all__'
        exclude = ('id_ingredient', 'id_recipe')

        labels = {
            'name_ingredient': 'Name Ingredient',
            'quantity': 'Quantity',
            'measurement_unit': 'Measurement Unit',
            'category_choices': 'Category Options',
            'name_category': 'Category',
            'name_new_category': 'New Category Name',
            'comment': 'Comment',
            'producer': 'Producer'
        }

    def __init__(self, *args, **kwargs):
        super(IngredientRecipeForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = 'POST'

        self.helper.layout = Layout(
            Row(Div('name_ingredient', css_class="col-6"), Div(InlineCheckboxes('category_choices'), css_class="col-6"),
                Div('name_category', css_class="col-6"), Div('name_new_category', css_class="col-6")),
            Row(Div('producer', css_class="col-3"), Div('comment', css_class="col-3"), ),
            Row(Div('quantity', css_class="col-3"), Div('measurement_unit', css_class="col-3"), )
        )


class AddInventoryForm(forms.ModelForm):
    class Meta:
        model = Inventory
        fields = ['name']
        labels = {
            'name': 'Name'
        }

    def __init__(self, *args, **kwargs):
        super(AddInventoryForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.layout = Layout(
            Row(Div('name', css_class="col-3"))
        )


class InventoryIngredientForm(forms.ModelForm):
    name_ingredient = forms.CharField(max_length=100)
    category_choices = forms.MultipleChoiceField(choices=CATEGORY_CHOICES, required=False,
                                                 widget=forms.CheckboxSelectMultiple)
    name_category = forms.ModelChoiceField(queryset=Category.objects.all(), empty_label='---')
    name_new_category = forms.CharField(max_length=100)
    measurement_unit = forms.ChoiceField(choices=MEASUREMENT_CHOICES, required=False)
    comment = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control form-control-sm'}), required=False)
    expiry_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)
    producer = forms.CharField(max_length=100, required=False)

    class Meta:
        model = InventoryIngredient
        fields = '__all__'
        exclude = ('id_ingredient', 'id_inventory', 'original_unit')

        labels = {
            'name_ingredient': 'Name Ingredient',
            'name_category': 'Category',
            'quantity': 'Quantity',
            'measurement_unit': 'Measurement Unit',
            'expiry_date': 'Expiry Date',
            'name_new_category': 'New Category Name',
            'category_choices': 'Category Options',
            'comment': 'Comment',
            'producer': 'Producer'
        }

    def __init__(self, *args, **kwargs):
        super(InventoryIngredientForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = 'POST'

        self.helper.layout = Layout(
            Row(Div('name_ingredient', css_class="col-6"), Div(InlineCheckboxes('category_choices'), css_class="col-6"),
                Div('name_category', css_class="col-6"), Div('name_new_category', css_class="col-6")),
            Row(Div('producer', css_class="col-3"), Div('comment', css_class="col-3"), ),
            Row(Div('quantity', css_class="col-3"), Div('measurement_unit', css_class="col-3"),
                Div('expiry_date', css_class="col-3"), )
        )


class PropertyIngredientForm(forms.Form):
    name = forms.CharField(label='Name',
                           widget=forms.TextInput(attrs={'class': 'form-control form-control-sm', }), )
    value = forms.DecimalField(label='Value',
                               widget=forms.NumberInput(attrs={'class': 'form-control form-control-sm'}))


class StepForm(forms.ModelForm):
    class Meta:
        model = Step
        fields = ('index', 'name', 'description')

        widgets = {
            'index': forms.NumberInput(attrs={'class': 'form-control form-control-s,'}),
            'name': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'description': forms.Textarea(attrs={'class': 'form-control form-control-sm'}),
        }

        labels = {
            'index': 'Index',
            'name': 'Name',
            'description': 'Description'
        }


class EquivalenceClassesForm(forms.ModelForm):
    basic_ingredient = forms.ModelChoiceField(queryset=Ingredient.objects.none())

    class Meta:
        model = EquivalentClass
        fields = ['name', 'description', 'basic_ingredient']
        labels = {
            'name': 'Name',
            'description': 'Description',
            'basic_ingredient': 'Basic Ingredient'
        }

    def __init__(self, *args, **kwargs):
        super(EquivalenceClassesForm, self).__init__(*args, **kwargs)

        instance = kwargs.get('instance')
        used_ingredients = EquivalentClass.objects.values_list('basic_ingredient', flat=True)
        if instance and instance.pk:
            available_ingredients = Ingredient.objects.exclude(id__in=used_ingredients).union(
                Ingredient.objects.filter(id=instance.basic_ingredient.id)
            )
        else:
            available_ingredients = Ingredient.objects.exclude(id__in=used_ingredients)

        self.fields['basic_ingredient'].queryset = available_ingredients

        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.layout = Layout(
            Row(Div('name', css_class="col-3"), Div('description', css_class="col-3"),
                Div('basic_ingredient', css_class="col-3"), )
        )


class ProportionForm(forms.ModelForm):
    class Meta:
        model = EquivalentClass_Ingredients
        fields = ['proportion']
        labels = {
            'proportion': 'Proportion'
        }

    def __init__(self, *args, **kwargs):
        super(ProportionForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.layout = Layout(
            Row(Div('proportion', css_class="col-3"))
        )


property_ingredient_formset = formset_factory(PropertyIngredientForm, extra=0, min_num=3, can_delete=True)
step_formset = formset_factory(StepForm, extra=0, min_num=1, can_delete=True)
