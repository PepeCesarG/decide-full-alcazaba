from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserChangeForm
from django.forms import ModelForm, DateInput, RadioSelect
from .models import UserProfile

class UserForm(ModelForm):

    class Meta:
        model = User
        fields = (
            'username',
        )

class DateInput(DateInput):
    input_type = 'date'


CHOICES=[('Male','Male'),
            ('Female','Female'),
            ('Other', 'Other')]

class UserProfileForm(ModelForm):
    class Meta:
        model = UserProfile
        fields = ('gender', 'birthdate')
        widgets = {
            'birthdate': DateInput(),
            'gender': RadioSelect(choices=CHOICES)
        }