
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.http import request

from foodshow import models
from .models import CustomUser, FoodData, Fridge


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email')
        help_texts = {
            'username': None,
            'password': None,
        }

    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'signup_username'})
        self.fields['email'].widget.attrs.update({'class': 'signup_email'})
        self.fields['password1'].widget.attrs.update({'class': 'signup_password1'},widget=forms.TextInput())
        self.fields['password2'].widget.attrs.update({'class': 'signup_password2'},widget=forms.TextInput())

        for fieldname in ['username', 'password1', 'password2']:
            self.fields[fieldname].help_text = None


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email')


class CustomFoodsForm(forms.ModelForm):
    class Meta:
        model = FoodData
        fields = ['food_name', 'days_good_for', 'food_category']



class CustomFridgeFoodsForm(forms.ModelForm):
    fooddata = forms.ModelChoiceField(queryset=None
                                              ,label="Add a custom food to the fridge", empty_label="pick a custom food")

    def __init__(self,user, *args, **kwargs):
        super(CustomFridgeFoodsForm, self).__init__(*args, **kwargs)
        self.fields['fooddata'].queryset = FoodData.objects.filter(user=user.id)

    class Meta:
        model = Fridge
        fields = ['fooddata']





class ShoppingForm(forms.ModelForm):
    foods = forms.ModelChoiceField(queryset=FoodData.objects.filter(user=0)
                                      ,label="Add a food to your shopping list", empty_label="pick a food")
    class Meta:
        model = FoodData
        fields = ['foods']
