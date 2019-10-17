from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from foodshow import models
from .models import CustomUser, FoodData, Fridge


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email')


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email')


class CustomFoodsForm(forms.ModelForm):
    class Meta:
        model = FoodData
        fields = ['food_name', 'days_good_for']


class CustomFridgeFoodsForm(forms.ModelForm):
    fooddata = forms.ModelChoiceField(queryset=FoodData.objects.filter(image_of_food="general.svg")
                                              ,empty_label="add a custom food to the fridge")

    class Meta:
        model = Fridge
        fields = ['fooddata']

# something wierd here.--- datanot moving in...
