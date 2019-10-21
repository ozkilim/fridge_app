import os
import random

import django
from faker import Faker

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodscan.settings')
import datetime

django.setup()

from foodshow.models import *

fake = Faker()



food_list = ["broccoli", "orange", "apple", "artichoke", "aubergine", "avacado", "banana", "cabbage", "carrot",
                 "cauliflour", "celery", "cherry", "chilli", "garlic", "ginger", "grapes", "lemon", "lettuce", "olives",
                 "onion", "pairs", "peach", "peas", "pepper", "pinapple", "potato", "pumpkin", "raddish", "raspberry",
                 "soybean", "strawberry", "sweetpotato", "tomato", "watermelon", "zuchinni"]

days_good_for_list =[4,40,30,7,20,5,6,23,28,15,28,8,20,140,60,9,55,6,80,55,20,15,5,24,40,70,60,15,4,20,4,50,6,5,11]

image_of_food_list =["broccoli.svg","orange.svg","apple.svg","artichoke.svg","aubergine.svg","avacado.svg","banana.svg","cabbage.svg","carrot.svg","cauliflour.svg","celery.svg","cherry.svg","chilli.svg","garlic.svg","ginger.svg","grapes.svg","lemon.svg","lettuce.svg","olives.svg","onion.svg","pairs.svg","peach.svg","peas.svg","pepper.svg","pinapple.svg","potato.svg","pumpkin.svg","raddish.svg","raspberry.svg","soybean.svg","strawberry.svg","sweetpotato.svg","tomato.svg","watermelon.svg","zuchinni.svg"]


catagory_list = ['vegetable','fruit', 'fruit','vegetable', 'vegetable','vegetable','fruit',
                 'vegetable','vegetable','vegetable','vegetable','fruit', 'vegetable','vegetable','vegetable','fruit'
                 'fruit','vegetable','vegetable','vegetable','fruit','fruit','vegetable','vegetable','fruit','vegetable','vegetable'
                 'vegetable','fruit','grain','fruit','vegetable','vegetable','fruit','vegetable','vegetable','vegetable']



def seed_food_data(number):
    for i in range(1, number):
        food_name = food_list[i]
        days_good_for = days_good_for_list[i]
        image_of_food = image_of_food_list[i]
        food_category = catagory_list[i]
        food = FoodData(id=i+1, food_name=food_name, days_good_for=days_good_for, image_of_food=image_of_food, food_category = food_category)
        food.save()
seed_food_data(35)
print("seeded!")



