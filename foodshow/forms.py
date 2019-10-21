from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

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
    fooddata = forms.ModelChoiceField(queryset=FoodData.objects.filter(image_of_food="general.svg")
                                              ,empty_label="Add a custom food to the fridge")

    class Meta:
        model = Fridge
        fields = ['fooddata']

# something wierd here.--- datanot moving in...
