from django.db import models
import shortuuid

class Project(models.Model):
    name = models.CharField(max_length=200)
    project_id = models.CharField(max_length=22, unique=True, editable=False)  # 22 is the length of a short UUID
    date_created = models.DateField(auto_now_add=True)
    programmed_by = models.CharField(max_length=200)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.project_id:
            self.project_id = shortuuid.uuid()
        super().save(*args, **kwargs)

class FormField(models.Model):
    FIELD_TYPES = (
        ('text', 'Text'),
        ('number', 'Number'),
        ('email', 'Email'),
        ('date', 'Date'),
    )

    project = models.ForeignKey(Project, related_name='fields', on_delete=models.CASCADE)
    field_name = models.CharField(max_length=200)
    field_type = models.CharField(max_length=20, choices=FIELD_TYPES)

    def __str__(self):
        return f"{self.field_name} ({self.field_type})"
