from django.contrib import admin
from .models import Project, FormField

class FormFieldInline(admin.TabularInline):
    model = FormField

class ProjectAdmin(admin.ModelAdmin):
    inlines = [FormFieldInline]
    list_display = ['name', 'project_id', 'programmed_by', 'date_created']

admin.site.register(Project, ProjectAdmin)
