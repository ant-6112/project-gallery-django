from django import forms
from .models import FormField

class FormFieldForm(forms.ModelForm):
    class Meta:
        model = FormField
        fields = ['name', 'type']

class FormFieldFormSet(forms.BaseFormSet):
    def clean(self):
        """Checks that no two fields have the same name or type."""
        if any(self.errors):
            return
        names = []
        types = []
        for form in self.forms:
            name = form.cleaned_data.get('name')
            type = form.cleaned_data.get('type')
            if name and type:
                if name in names:
                    raise forms.ValidationError("Fields in a form must have distinct names.")
                names.append(name)

                if type not in ['char', 'text']:
                    raise forms.ValidationError("Invalid field type submitted.")
                
class DynamicForm(forms.Form):
    def __init__(self, *args, **kwargs):
        form_fields = kwargs.pop('form_fields', None)
        super(DynamicForm, self).__init__(*args, **kwargs)
        if form_fields:
            for field in form_fields:
                if field.type == 'char':
                    self.fields[field.name] = forms.CharField(max_length=200)
                elif field.type == 'text':
                    self.fields[field.name] = forms.TextField()