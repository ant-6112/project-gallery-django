from .models import Field,Project
from django import forms

class ProjectMaker(forms.ModelForm):
    class Meta:
        model = Project
        fields = (
            'name',
        )

class FormDy(forms.ModelForm):
    class Meta:
        model = Field
        fields = (
            'fieldname','fieldtype','projectForm'
        )
        widgets = {
            'fieldname': forms.TextInput(attrs={'class' : 'form-control'}),
            'fieldtype': forms.TextInput(attrs={'class' : 'form-control'}),
            'projectForm': forms.Select(attrs={'class' : 'form-control'}),
        }

class DynamicForm(forms.Form):
    def __init__(self, *args, **kwargs):
        form_fields = kwargs.pop('form_fields', None)
        super(DynamicForm, self).__init__(*args, **kwargs)
        if form_fields:
            for field in form_fields:
                if field.fieldtype == 'char':
                    self.fields[field.fieldname] = forms.CharField(max_length=200)
                elif field.fieldtype == 'text':
                    self.fields[field.fieldname] = forms.TextField()