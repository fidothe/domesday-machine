from django import forms
from django.forms import ModelForm
from domes.models import EmailSignup

class EmailSignupForm(ModelForm):
    class Meta:
        model = EmailSignup

class TranslateForm(forms.Form):
    transcription = forms.CharField(widget=forms.Textarea, min_length=5)
