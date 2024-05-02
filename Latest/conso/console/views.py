from django import forms
from django.shortcuts import render, redirect
from django.http import JsonResponse,HttpResponse
from .models import Field,Project
from .forms import DynamicForm,FormDy,ProjectMaker
import time

def index(request):
    context = {'form': FormDy(),'fields': Field.objects.all()}
    return render(request, 'console/index.html',context)

def create_project(request):
    if request.method == 'POST':
        form = ProjectMaker(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')

    return render(request, 'console/form2.html',{'form': ProjectMaker()})

def create_field(request):
    if request.method == 'POST':
        form = FormDy(request.POST or None)
        if form.is_valid():
            field = form.save()
            context = {'field': field}
            return render(request, 'console/field.html',context)

    return render(request, 'console/form.html',{'form': FormDy()})


def form_page(request, form_id):
    form_instance = Project.objects.get(id=form_id)
    form_fields = Field.objects.filter(projectForm_id=1)
    form = DynamicForm(form_fields=form_fields)
    return render(request, 'console/form_page.html', {'form': form})

