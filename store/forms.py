from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ('email',)

class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Username',
        'id': 'username-input'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Password',
        'id': 'password-input'
    }))

class ShippingForm(forms.Form):
    shipping_name = forms.CharField(
        max_length=255, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name', 'id': 'shipping-name'})
    )
    shipping_address = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Street Address', 'id': 'shipping-address'}),
        required=True
    )
    shipping_city = forms.CharField(
        max_length=100, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City', 'id': 'shipping-city'})
    )
    shipping_postal_code = forms.CharField(
        max_length=20, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Postal/ZIP Code', 'id': 'shipping-postal-code'})
    )
    shipping_country = forms.CharField(
        max_length=100, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Country', 'id': 'shipping-country'})
    )
