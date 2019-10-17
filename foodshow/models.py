from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.
class CustomUser(AbstractUser):
    pass

    def __str__(self):
        return self.email


class FoodData(models.Model):
    food_name = models.CharField(max_length=100)
    days_good_for = models.IntegerField()
    image_of_food = models.ImageField(upload_to='media/food_icons/', default='general.svg', null=True, blank=True)

    def __str__(self):
        return self.food_name


class Fridge(models.Model):
    fooddata = models.ForeignKey(FoodData, on_delete=models.CASCADE)
    date_scanned = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)
