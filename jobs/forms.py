from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile, SECURITY_QUESTIONS
import random

class CustomUserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=10, required=True)
    security_question = forms.ChoiceField(
        choices=SECURITY_QUESTIONS,
        label="Select Security Question"
    )

    security_answer = forms.CharField(
        max_length=200,
        widget=forms.PasswordInput(),
        label="Security Answer"
    )



    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

class UsernameForm(forms.Form):
    username = forms.CharField()

class SecurityAnswerForm(forms.Form):
    answer = forms.CharField(widget=forms.PasswordInput)

class NewPasswordForm(forms.Form):
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("password1") != cleaned_data.get("password2"):
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data
    
from .models import UserProfile

class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = '__all__'