from django import forms
from .models import *

class UserForm(forms.ModelForm):
    # Input fields
    username = forms.CharField(required=True, widget=forms.TextInput(attrs={
        'maxlength': '30', 'size': '50', 'autofocus': 'autofocus', 'autocomplete': 'off'
    }))
    email = forms.CharField(required=True, widget=forms.TextInput(attrs={
        'maxlength': '50', 'size': '50', 'autocomplete': 'off'
    }))
    password = forms.CharField(required=True, widget=forms.PasswordInput(attrs={
        'maxlength': '50', 'size': '50'
    }))

    def __init__(self, *args, **kwargs):
        super(forms.ModelForm, self).__init__(*args, **kwargs)
        self.fields['username'].help_text = None
        
    class Meta:
        model = UserProfile
        fields = ('username', 'email', 'password')
        
    # Check for duplicate emails
    def clean_email(self):
        email = self.cleaned_data["email"]
        try:
            UserProfile._default_manager.get(email=email)
        except UserProfile.DoesNotExist:
            return email
        raise forms.ValidationError("An account with this email already exists.")

    # Save the user (as inactive, pending email confirmation)
    def save(self, commit=True):
        user = super(UserForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password"])
        
        user.email = self.cleaned_data['email']
        if commit:
            user.is_active = False
            user.save()

        return user
        
class LeagueForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={
        'maxlength': '50', 'size': '50', 'autofocus': 'autofocus', 'autocomplete': 'off'
    }))
    number_of_picks = forms.IntegerField(widget=forms.NumberInput(attrs={
        'min': '1', 'max': '10', 'step': '1', 'autocomplete': 'off'
    }))
    random_order = forms.BooleanField(required=False)
    snake_style = forms.BooleanField(required=False)
    
    def __init__(self, *args, **kwargs):
        super(forms.ModelForm, self).__init__(*args, **kwargs)
        self.fields['number_of_picks'].label = "Number of picks (max: 10)"
        self.fields['random_order'].label = "Random order? (default: determined by bidding)"
        self.fields['snake_style'].label = "Snake style?"
    
    class Meta:
        model = League
        fields = ('name', 'number_of_picks', 'random_order', 'snake_style')
