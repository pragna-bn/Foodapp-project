
 # Create your models here.
from django.db import models

class Restaurant(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=200, blank=True)
    image = models.ImageField(upload_to='restaurants/', blank=True, null=True)
    is_popular = models.BooleanField(default=False)

    def __str__(self):
        return self.name