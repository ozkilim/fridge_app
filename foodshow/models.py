from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.
class CustomUser(AbstractUser):
    send_daily_emails = models.BooleanField(default=False)


    def __str__(self):
        return self.email


class FoodData(models.Model):
    CATEGORIES = (
        ('fruit', 'fruit'),
        ('vegetable', 'vegetable'),
        ('meat', 'meat'),
        ('fish', 'fish'),
        ('dairy', 'dairy'),
        ('grain', 'grain'),
        ('other', 'other'),
    )
    food_name = models.CharField(max_length=100)
    days_good_for = models.PositiveIntegerField()
    image_of_food = models.ImageField(upload_to='media/food_icons/', default='general.svg', null=True, blank=True)
    food_category = models.CharField(max_length=30, choices=CATEGORIES)
    user = models.PositiveIntegerField()


    def __str__(self):
        return self.food_name


class Fridge(models.Model):
    fooddata = models.ForeignKey(FoodData, on_delete=models.CASCADE)
    date_scanned = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)




