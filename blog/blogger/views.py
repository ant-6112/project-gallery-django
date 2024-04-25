from django import forms
from django.shortcuts import render, redirect
from .models import field,Form
from .forms import DynamicForm,FormDy,FormMaker


def index(request):
    context = {'form': FormDy()}
    return render(request, 'blogger/index.html',context)

def create_form(request):
    if request.method == 'POST':
        form = FormMaker(request.POST or None)
        if form.is_valid():
            form.save()
            return redirect('create_field')

    return render(request, 'blogger/form2.html',{'form': FormMaker()})

def create_field(request):
    if request.method == 'POST':
        form = FormDy(request.POST or None)
        if form.is_valid():
            field = form.save()
            context = {'field': field}
            return render(request, 'blogger/field.html',context)

    return render(request, 'blogger/form.html',{'form': FormDy()})

"""
def form_creator(request):
    FormSet = forms.formset_factory(FormFieldForm, formset=FormFieldFormSet, extra=1)
    if request.method == 'POST':
        formset = FormSet(request.POST)
        if formset.is_valid():
            form = Form.objects.create(name='New Form')
            for form_field_form in formset:
                form_field = form_field_form.save(commit=False)
                form_field.form = form
                form_field.save()
            # Redirect to the new form page
            return redirect('form_page', form_id=form.id)
    else:
        formset = FormSet()
    return render(request, 'blogger/form_creator.html', {'formset': formset})

def form_creator(request):
    FormSet = forms.formset_factory(FormFieldForm, formset=FormFieldFormSet, extra=1 )
    if request.method == 'POST':
        formset = FormSet(request.POST)
        if formset.is_valid():
            form_fields = []
            for form in formset:
                form_field = form.save()
                form_fields.append(form_field)
            # Redirect to the new form page
            return redirect('form_page', form_id=form_fields[0].id)
    else:
        formset = FormSet()
    return render(request, 'blogger/form_creator.html', {'formset': formset})
"""

def form_page(request, form_id):
    form_instance = Form.objects.get(id=form_id)
    form_fields = form_instance.fields.all()
    form = DynamicForm(form_fields=form_fields)
    return render(request, 'blogger/form_page.html', {'form': form})

"""
    if request.method == 'POST':
        if form.is_valid():
            form_data = FormData(form=form_instance, data=form.cleaned_data)
            form_data.save()
            return HttpResponseRedirect('/thanks/')  # Redirect after POST
"""