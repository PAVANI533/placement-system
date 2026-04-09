from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile, SECURITY_QUESTIONS
import random

class CustomUserRegisterForm(UserCreationForm):

    security_question = forms.ChoiceField(
        choices=SECURITY_QUESTIONS,
        label="Select Security Question"
    )

    security_answer = forms.CharField(
        max_length=200,
        widget=forms.PasswordInput(),
        label="Security Answer"
    )

    # captcha = forms.IntegerField(label="")

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)

        # # Dynamic CAPTCHA
        # self.num1 = random.randint(1, 10)
        # self.num2 = random.randint(1, 10)
        # self.fields['captcha'].label = f"What is {self.num1} + {self.num2}?"


    def save(self, commit=True):
        user = super().save(commit)

        from .models import UserProfile

    # ✅ FIX: use get_or_create instead of create
        profile, created = UserProfile.objects.get_or_create(user=user)

        profile.security_question = self.cleaned_data["security_question"]
        profile.security_answer = self.cleaned_data["security_answer"]
        profile.save()

        return user
    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name", "password1", "password2"]

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
    
from django import forms
from .models import UserProfile

class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = '__all__'