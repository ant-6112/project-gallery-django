from django.db import models

class MergeRequest(models.Model):
    file1 = models.FileField(upload_to='uploads/')
    file2 = models.FileField(upload_to='uploads/')