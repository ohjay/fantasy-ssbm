from django import forms
from .models import *

class UserForm(forms.ModelForm):
    # Input fields
    username = forms.CharField(widget=forms.TextInput(attrs={
        'maxlength': '30', 'size': '50', 'autofocus': 'autofocus'
    }))
    email = forms.CharField(widget=forms.TextInput(attrs={
        'maxlength': '50', 'size': '50'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'maxlength': '50', 'size': '50'
    }))

    def __init__(self, *args, **kwargs):
        super(forms.ModelForm, self).__init__(*args, **kwargs)
        self.fields['username'].help_text = None
        
    class Meta:
        model = UserProfile
        fields = ('username', 'email', 'password')
        
class LeagueForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(attrs={
        'maxlength': '50', 'size': '50', 'autofocus': 'autofocus'
    }))
    number_of_picks = forms.IntegerField(widget=forms.NumberInput(attrs={
        'min': '1', 'max': '10', 'step': '1'
    }))
    
    def __init__(self, *args, **kwargs):
        super(forms.ModelForm, self).__init__(*args, **kwargs)
        self.fields['number_of_picks'].label = "Number of picks (max: 10)"
    
    class Meta:
        model = League
        fields = ('name', 'number_of_picks')
