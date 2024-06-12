from django.urls import path
from . import views

urlpatterns = [
    path('', views.project_list, name='project_list'),
    path('add_project/', views.add_project, name='add_project'),
    path('add_field/<int:project_id>/', views.add_field, name='add_field'),
    path('project_form/<int:project_id>/', views.project_form, name='project_form'),
]
