from django.urls import path
from .views import merge_excel, preview_file

app_name = 'merger'

urlpatterns = [
    path('merge/', merge_excel, name='merge_excel'),
    path('preview/<int:pk>/<str:field>/', preview_file, name='preview_file'),
]