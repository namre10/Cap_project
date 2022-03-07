from email.headerregistry import Address
from tokenize import Name
from django.db import models

# Create your models here.

class GeneralData(models.Model):
    water_consumption = models.IntegerField()
    calories_burnt = models.IntegerField()

    class Meta:
        verbose_name_plural = 'General Data'

    def __str__(self):
        return f'{self.water_consumption}--{self.calories_burnt}'



