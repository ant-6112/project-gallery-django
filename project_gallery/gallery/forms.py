from django import forms
from .models import Project, FormField

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'programmed_by']

class FormFieldForm(forms.ModelForm):
    class Meta:
        model = FormField
        fields = ['field_name', 'field_type']

""""
def dynamic_form(fields):
    form = forms.Form()
    for field in fields:
        if field.field_type == 'text':
            form.fields[field.field_name] = forms.CharField(label=field.field_name, max_length=200)
        elif field.field_type == 'number':
            form.fields[field.field_name] = forms.IntegerField(label=field.field_name)
        elif field.field_type == 'email':
            form.fields[field.field_name] = forms.EmailField(label=field.field_name)
        elif field.field_type == 'date':
            form.fields[field.field_name] = forms.DateField(label=field.field_name, widget=forms.DateInput(attrs={'type': 'date'}))
    return form
"""

def dynamic_form(fields):
    class DynamicForm(forms.Form):
        def __init__(self, *args, **kwargs):
            super(DynamicForm, self).__init__(*args, **kwargs)
            for field in fields:
                if field.field_type == 'text':
                    self.fields[field.field_name] = forms.CharField(label=field.field_name, max_length=200)
                elif field.field_type == 'number':
                    self.fields[field.field_name] = forms.IntegerField(label=field.field_name)
                elif field.field_type == 'email':
                    self.fields[field.field_name] = forms.EmailField(label=field.field_name)
                elif field.field_type == 'date':
                    self.fields[field.field_name] = forms.DateField(label=field.field_name, widget=forms.DateInput(attrs={'type': 'date'}))
    return DynamicForm
