from django.db import models

class Project(models.Model):
    name = models.CharField(max_length=128)

    def __str__(self):
        return self.name

class Field(models.Model):
    fieldname = models.CharField(max_length=128)
    fieldtype = models.CharField(max_length=128)
    projectForm = models.ForeignKey(Project, on_delete=models.CASCADE)

    def __str__(self):
        return self.fieldname
