from django.contrib import admin
from django.urls import path
from merger.views import home, merge_excel

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('merge/', merge_excel, name='merge_excel'),
]