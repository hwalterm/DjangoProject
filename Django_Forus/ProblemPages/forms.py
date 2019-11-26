from django import forms
from .models import Problems

class CreatePage(forms.ModelForm):

    class Meta:
        model = Problems
        fields =['name','parent','page_admins', 'id', 'description']
        widgets = {'page_admins': forms.HiddenInput(),
                   'parent':forms.HiddenInput}

