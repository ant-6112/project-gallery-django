from django.db import models

class Form(models.Model):
    name = models.CharField(max_length=200)

class FormField(models.Model):
    name = models.CharField(max_length=200)
    type = models.CharField(max_length=200)
    form = models.ForeignKey(Form, related_name='fields', on_delete=models.CASCADE)

"""
class FormData(models.Model):
    form = models.ForeignKey(Form, on_delete=models.CASCADE)
    data = JSONField()
"""