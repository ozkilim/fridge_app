import datetime
from email import message
from email.message import EmailMessage

import pytz
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.http import request

from foodshow.models import CustomUser, Fridge, FoodData


class Command(BaseCommand):
    help = 'Displays current time'

    def handle(self, *args, **kwargs):

        user_list = CustomUser.objects.all()

        for user in user_list:
            if user.send_daily_emails == True:
                foods_to_eat_today_list = []
                fridge_foods = Fridge.objects.filter(user_id=user.id)
                for one_food in fridge_foods:
                    if one_food.used == False:
                        get_food_id = int(one_food.fooddata_id)
                        this_food = FoodData.objects.get(id=get_food_id)
                        good_for = this_food.days_good_for
                        foodname = FoodData.objects.get(id=get_food_id).food_name
                        scanneddate = one_food.date_scanned
                        end_date = scanneddate + datetime.timedelta(days=good_for)
                        utc = pytz.UTC
                        now = utc.localize(datetime.datetime.now())
                        time_left = end_date - now
                        days_left = time_left.days
                        if days_left == 0:
                            foods_to_eat_today_list.append(foodname)
                print(foods_to_eat_today_list)

                mail_subject = 'Food to be eaten today! Dont waste this great food'
                message =', '.join(foods_to_eat_today_list)
                user_email = user.email
                send_mail(
                    mail_subject,
                    message,
                    'fridgeflipapp@gmail.com',
                    [user_email],
                    fail_silently=False,
                )
                print('email sent to')
                print(user_email)


