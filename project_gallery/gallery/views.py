from django.shortcuts import render, get_object_or_404, redirect
from .models import Project, FormField
from .forms import ProjectForm, FormFieldForm, dynamic_form
import importlib
import os

def project_list(request):
    projects = Project.objects.all()
    return render(request, 'gallery/project_list.html', {'projects': projects})

def add_project(request):
    if request.method == 'POST':
        project_form = ProjectForm(request.POST)
        if project_form.is_valid():
            project = project_form.save()
            return redirect('add_field', project_id=project.id)
    else:
        project_form = ProjectForm()
    return render(request, 'gallery/add_project.html', {'project_form': project_form})

def add_field(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if request.method == 'POST':
        field_form = FormFieldForm(request.POST)
        if field_form.is_valid():
            field = field_form.save(commit=False)
            field.project = project
            field.save()
            return redirect('add_field', project_id=project.id)
    else:
        field_form = FormFieldForm()
    return render(request, 'gallery/add_field.html', {'project': project, 'field_form': field_form, 'fields': project.fields.all()})

def project_form(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    fields = project.fields.all()
    form_class = dynamic_form(fields)
    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            form_data = {field.field_name: form.cleaned_data[field.field_name] for field in fields}
            script_path = os.path.join('gallery', 'scripts', f"{project.name}.py")
            module = importlib.import_module(script_path.replace('/', '.'))
            return redirect('project_list')
    else:
        form = form_class()
    return render(request, 'gallery/project_form.html', {'project': project, 'form': form})
