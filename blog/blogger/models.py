from django.db import models

class Form(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class field(models.Model):
    fieldname = models.CharField(max_length=128)
    fieldtype = models.CharField(max_length=128)
    projectForm = models.ForeignKey(Form, related_name='fields', on_delete=models.CASCADE)

    def __str__(self):
        return self.fieldname
    