import django.forms
from django.forms import ModelForm
from domes.models import EmailSignup

class EmailSignupForm(ModelForm):
    class Meta:
        model = EmailSignup

