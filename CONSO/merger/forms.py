from django import forms
from .models import MergeRequest

class MergeRequestForm(forms.ModelForm):
    class Meta:
        model = MergeRequest
        fields = ['file1', 'file2']