from __future__ import unicode_literals

import base64
from PIL import Image
from io import BytesIO
import datetime
import re
import json
from pyexpat.errors import messages

import pytz
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.postgres import serializers
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.http import HttpResponse, request
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from foodscan.middleware.login_exempt import login_exempt
from foodshow.forms import CustomUserCreationForm, CustomFoodsForm, CustomFridgeFoodsForm, ShoppingForm
from foodshow.models import Fridge, FoodData, CustomUser
from foodshow.ocr_core import ocr_core
from foodshow.tokens import account_activation_token




UPLOAD_FOLDER = '/static/uploads/'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

@login_exempt
def landing(request):
    return render(request, 'landing.html')

@login_exempt
def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_patient = True
            user.is_active = False
            user.save()
            '''hashing process here to give link'''
            current_site = get_current_site(request)
            mail_subject = 'Activate your account.'
            message = render_to_string('acc_active_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(
                mail_subject, message, to=[to_email]
            )
            email.send()
            return render(request, 'confirm.html'
                )  # should redirect to dead end page until user confirms email
    else:
        form = CustomUserCreationForm()
    return render(request, 'signup.html', {'form': form})


@login_exempt
def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        # flash message saying thanks
        return redirect('foodshow:index')
    else:
        return HttpResponse('Activation link is invalid!')
# the list will come in from the cam module...

def fridge_filler(request, extracted_text):
    # however it splits assuming perfect spacing.... more work needed here to clean real data...
    print(extracted_text)
    shopping_list = re.sub("[^\w]", " ", extracted_text.lower()).split()
    print(shopping_list)
    food_id_list = []
    for food_name in shopping_list:
        database_food = FoodData.objects.filter(food_name=food_name).first()
        # its a set of one and so we need to go inside the query set
        if database_food is not None:
            food_id_list.append(database_food.id)
    print(food_id_list)
    # still this function is adding it the list two times ...
    for i in food_id_list:
        food = Fridge(used=False, fooddata_id=i, user_id=request.user.id)
        food.save()

    return redirect('foodshow:index')




def index(request):
    fridge_foods = Fridge.objects.filter(user_id=request.user)
    food_list = []
    if request.method == 'POST':
        eaten_food = request.POST.get('submit')
        get_eaten_food_from_fridge = Fridge.objects.get(id=eaten_food)
        get_eaten_food_from_fridge.used = True
        get_eaten_food_from_fridge.save()

    for one_food in fridge_foods:
        if one_food.used == False:
            get_food_id = int(one_food.fooddata_id)
            this_food = FoodData.objects.get(id=get_food_id)
            good_for = this_food.days_good_for
            foodname = FoodData.objects.get(id=get_food_id).food_name
            food_image = FoodData.objects.get(id=get_food_id).image_of_food
            scanneddate = one_food.date_scanned
            end_date = scanneddate + datetime.timedelta(days=good_for)
            utc = pytz.UTC
            now = utc.localize(datetime.datetime.now())
            time_left = end_date - now
            days_left = time_left.days

            if days_left < 0:
                one_food.delete()
                # small cleaner code for any over due food to not clog up fridge database... this info may want to be kept for data analysis later down the line..
            if days_left == 0:
                days_left = "Eatme Today"
            elif days_left == 1:
                days_left = "Eat Tomorrow"
            elif days_left == 2:
                days_left = "2 days left to eat"
            elif days_left == 3:
                days_left = "3 days left to eat"
            elif days_left == 4:
                days_left = "4 days left to eat"
            elif days_left == 5:
                days_left = "5 days left to eat"
            elif days_left == 6:
                days_left = "6 days left to eat"
            elif days_left == 7:
                days_left = "7 days left to eat"
            elif days_left == 8:
                days_left = "8 days left to eat"
            elif days_left >= 9:
                days_left = "Over 8 days left to eat"

            fridge_food_id = one_food.id

            food_list.append({"foodname": foodname, "scanneddate": scanneddate, "days_left": days_left,
                              "fridge_food_id": fridge_food_id, "food_image": food_image})

    day_list = ["Eatme Today", "Eat Tomorrow", "2 days left to eat", "3 days left to eat", "4 days left to eat", "5 days left to eat", "6 days left to eat", "7 days left to eat", "8 days left to eat", "Over 8 days left to eat"]
    return render(request, "index.html", {"food_list": food_list, "day_list": day_list})


def sort_by_catagory(request):
    fridge_foods = Fridge.objects.filter(user_id=request.user)
    food_list = []
    if request.method == 'POST':
        eaten_food = request.POST.get('submit')
        get_eaten_food_from_fridge = Fridge.objects.get(id=eaten_food)
        get_eaten_food_from_fridge.used = True
        get_eaten_food_from_fridge.save()
    for one_food in fridge_foods:
        if one_food.used == False:
            get_food_id = int(one_food.fooddata_id)
            this_food = FoodData.objects.get(id=get_food_id)
            good_for = this_food.days_good_for
            foodname = FoodData.objects.get(id=get_food_id).food_name
            food_image = FoodData.objects.get(id=get_food_id).image_of_food
            scanneddate = one_food.date_scanned
            end_date = scanneddate + datetime.timedelta(days=good_for)
            utc = pytz.UTC
            now = utc.localize(datetime.datetime.now())
            time_left = end_date - now
            days_left = time_left.days
            fridge_food_id = one_food.id
            food_catagory = FoodData.objects.get(id=get_food_id).food_category
            food_list.append({"foodname": foodname, "scanneddate": scanneddate, "days_left": days_left,
                              "fridge_food_id": fridge_food_id, "food_image": food_image , "food_catagory":food_catagory})
# chagne logic here or sorting!

    food_catagory_list = ["dairy", "fruit", "vegetable", "meat", "fish", "grain", "other"]
    return render(request, "index_by__food_catagory.html", {"food_list": food_list, "food_catagory_list": food_catagory_list})



def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def upload_page(request):
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.FILES:
            msg = 'No file selected'
            return render(request, 'upload.html', {"msg":msg})
        file = request.FILES['file']
            # if user does not select file, browser also
            # submit a empty part without filename
        if file.name == '':
            msg = 'No file selected'
            return render(request, 'upload.html', {"msg":msg})

        if file and allowed_file(file.name):
                # default_storage.save(os.path.join(os.getcwd() + UPLOAD_FOLDER, file.name), file)

                # call the OCR function on it
            extracted_text = ocr_core(file)

                # extract the text and display it
                # then make user say yes or no.../correct the text...?
                # text correction/edits could take place here
                # before redirect show the message...
            trial_output = str(extracted_text)
            return render(request ,"upload.html", {"trial_output":trial_output})

    elif request.method == 'GET':

        return render(request, 'upload.html')


def eaten(request):
    if request.method == 'POST':
        if 'submit' in request.POST:
            non_eaten_food_id = request.POST.get('submit')
            get_eaten_food_from_fridge = Fridge.objects.get(id=non_eaten_food_id)
            get_eaten_food_from_fridge.used = False
            get_eaten_food_from_fridge.save()

        elif 'delete_foods' in request.POST:
            Fridge.objects.filter(used=True).delete()

    fridge_foods = Fridge.objects.filter(user_id=request.user)
    eaten_foods = []
    for one_food in fridge_foods:
        get_food_id = int(one_food.fooddata_id)
        foodname = FoodData.objects.get(id=get_food_id).food_name
        fridge_food_id = one_food.id
        food_image = FoodData.objects.get(id=get_food_id).image_of_food
        if one_food.used == True:
            eaten_foods.append({"foodname": foodname, "fridge_food_id": fridge_food_id, "food_image": food_image})

    return render(request, 'eaten.html', {"eaten_foods": eaten_foods})


# class VideoCamera(object):
#     def __init__(self):
#         # Using OpenCV to capture from device 0. If you have trouble capturing
#         # from a webcam, comment the line below out and use a video file
#         # instead.
#         self.video = cv2.VideoCapture(0)
#         # If you decide to use video.mp4, you must have this file in the folder
#         # as the main.py.
#         # self.video = cv2.VideoCapture('video.mp4')
#
#     def __del__(self):
#         self.video.release()
#
#     def get_frame(self):
#         success, image = self.video.read()
#         # We are using Motion JPEG, but OpenCV defaults to capture raw images,
#         # so we must encode it into JPEG in order to correctly display the
#         # video stream.
#
#         # _, frame = cap.read()
#         decodedObjects = pyzbar.decode(image)
#         thedata = None
#         for obj in decodedObjects:
#             print("Data", obj.data)
#             # this is the print...
#             thedata = obj.data
#         ret, jpeg = cv2.imencode('.jpg', image)
#
#         return jpeg.tobytes(), thedata
#
#
# def gen(camera):
#     while True:
#         frame = camera.get_frame()[0]
#         yield (b'--frame\r\n'
#                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
#         if camera.get_frame()[1] is not None:
#             return render(request, "index.html")




def custom_foods(request):
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = CustomFoodsForm(request.POST)
        if form.is_valid():
            for foodobj in FoodData.objects.all():
                if form.cleaned_data["food_name"] == foodobj.food_name:
                    error = "This is not a custom food, add it from our data base of foods!"
                    return render(request, "custom_foods.html", {"error": error})
                    break
            obj = form.save(commit=False)
            obj.user = request.user.id
            obj.save()
            return render(request, "custom_foods.html")
    else:
        form = CustomFoodsForm()
    return render(request, "custom_foods.html", {"form": form})


def fridge_manager(request):
    # only problem is that it resets when you pass through each time...
    if request.method == 'POST':
        if "clear-custom-foods-added" in request.POST:
            data = {"food_added_list":[]}
            with open('customfoods.txt', 'w') as outfile:
                json.dump(data, outfile)
            return redirect("foodshow:index")
        # create a form instance and populate it with data from the request:
        form = CustomFridgeFoodsForm(user=request.user, data =request.POST)
        with open('customfoods.txt') as json_file:
            context = json.load(json_file)
        food_added_list = context["food_added_list"]
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user_id = request.user.id
            obj.save()
            x = form.save(commit=False)
            foodid =x.fooddata_id
            thisfood = FoodData.objects.get(id=foodid).food_name
            food_added_list.append(thisfood)
            data = {"food_added_list":food_added_list}
            with open('customfoods.txt', 'w') as outfile:
                json.dump(data, outfile)
        return redirect("foodshow:fridge_manager")
    else:
        with open('customfoods.txt') as json_file:
            context = json.load(json_file)
        passinlist = context["food_added_list"]
        form = CustomFridgeFoodsForm(user=request.user)

    return render(request, "fridge_manager.html", {"form": form, "passinlist":passinlist})



def fullfoodshow(request):
    get_all_foods = FoodData.objects.all()
    food_data_list = []
    for foodobj in get_all_foods:
        if foodobj.image_of_food != "general.svg":
            food_icon = foodobj.image_of_food
            food_id = foodobj.id
            food_category = foodobj.food_category
            food_data_list.append({"food_icon":food_icon,"food_id":food_id, "food_category":food_category })
    return render(request, "fullfoodshow.html" ,{"food_data":food_data_list})

def pushsettings(request):

    initial_status = CustomUser.objects.get(id=request.user.id).send_daily_emails
    return render(request, "pushsettings.html" ,{"send_daily_emails":initial_status})

def toggle(request):
    w = CustomUser.objects.get(id=request.user.id)
    w.send_daily_emails = request.POST['isworking'] == 'true'
    w.save()

    return HttpResponse('success')

def shopping(request):
    with open('shopping_list.txt') as json_file:
        context = json.load(json_file)
    shopping_list = context["shopping_list"]
    if "clear_shopping_list" in request.POST:
        data = {"shopping_list": []}
        with open('shopping_list.txt', 'w') as outfile:
            json.dump(data, outfile)
        return redirect("foodshow:index")

    elif request.method == 'POST':
        if 'delete_from_shopping_list' in request.POST:
            delete_food = request.POST.get('delete_from_shopping_list')

            shopping_list.remove(delete_food)

            data = {"shopping_list": shopping_list}
            with open('shopping_list.txt', 'w') as outfile:
                json.dump(data, outfile)
        else:
            form = ShoppingForm(request.POST)
            if form.is_valid():

                x = form.cleaned_data
                foodobj =x['foods']
                thisfood = foodobj.food_name
                shopping_list.append(thisfood)
                data = {"shopping_list":shopping_list}
                with open('shopping_list.txt', 'w') as outfile:
                    json.dump(data, outfile)

    else:
        with open('shopping_list.txt') as json_file:
            context = json.load(json_file)
        shopping_list = context["shopping_list"]

    form = ShoppingForm()

    return render(request, "shopping.html",{"form":form, "shopping_list":shopping_list})




def seed(request):
    food_list = ["broccoli", "orange", "apple", "artichoke", "aubergine", "avacado", "banana", "cabbage", "carrot",
                 "cauliflour", "celery", "cherry", "chilli", "garlic", "ginger", "grapes", "lemon", "lettuce", "olives",
                 "onion", "pairs", "peach", "peas", "pepper", "pinapple", "potato", "pumpkin", "raddish", "raspberry",
                 "soybean", "strawberry", "sweetpotato", "tomato", "watermelon", "zuchinni"]

    days_good_for_list = [4, 40, 30, 7, 20, 5, 6, 23, 28, 15, 28, 8, 20, 140, 60, 9, 55, 6, 80, 55, 20, 15, 5, 24, 40,
                          70, 60, 15, 4, 20, 4, 50, 6, 5, 11]

    image_of_food_list = ["broccoli.svg", "orange.svg", "apple.svg", "artichoke.svg", "aubergine.svg", "avacado.svg",
                          "banana.svg", "cabbage.svg", "carrot.svg", "cauliflour.svg", "celery.svg", "cherry.svg",
                          "chilli.svg", "garlic.svg", "ginger.svg", "grapes.svg", "lemon.svg", "lettuce.svg",
                          "olives.svg", "onion.svg", "pairs.svg", "peach.svg", "peas.svg", "pepper.svg", "pinapple.svg",
                          "potato.svg", "pumpkin.svg", "raddish.svg", "raspberry.svg", "soybean.svg", "strawberry.svg",
                          "sweetpotato.svg", "tomato.svg", "watermelon.svg", "zuchinni.svg"]

    catagory_list = ['vegetable', 'fruit', 'fruit', 'vegetable', 'vegetable', 'vegetable', 'fruit',
                     'vegetable', 'vegetable', 'vegetable', 'vegetable', 'fruit', 'vegetable', 'vegetable', 'vegetable',
                     'fruit'
                     'fruit', 'vegetable', 'vegetable', 'vegetable', 'fruit', 'fruit', 'vegetable', 'vegetable',
                     'fruit', 'vegetable', 'vegetable'
                                           'vegetable', 'fruit', 'grain', 'fruit', 'vegetable', 'vegetable', 'fruit',
                     'vegetable', 'vegetable', 'vegetable']

    def seed_food_data(number):
        for i in range(1, number):
            food_name = food_list[i]
            days_good_for = days_good_for_list[i]
            image_of_food = image_of_food_list[i]
            food_category = catagory_list[i]
            food = FoodData(id=i + 1, food_name=food_name, days_good_for=days_good_for, image_of_food=image_of_food,
                            food_category=food_category, user=0)
            food.save()

    seed_food_data(35)
    return HttpResponse('seeded')

# def scan_in_progress(request):
#
#
#     return render(request, "scan_in_progress.html")


from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from django.views.generic import TemplateView



def upload_file(image):
    fs = FileSystemStorage()
    filename = fs.save(image.name, image)
    uploaded_file_url = fs.path(filename)
    return uploaded_file_url


class ImageFaceDetect(TemplateView):
    template_name = 'image.html'
    def post(self, request, *args, **kwargs):
        data = request.POST.get('image')
        print(data)
        clean_data = data.replace("data:image/png;base64,", "")
        print(clean_data)
        import base64
        bytes_base64 = clean_data.encode()
        data = base64.b64decode(bytes_base64)
        open('image_analysis/image.png', 'wb').write(data)
        extracted_text = ocr_core('image_analysis/image.png')
        trial_output = str(extracted_text)
        print(trial_output)
        return JsonResponse(status=200, data={'image': trial_output, 'message': trial_output})



class LiveVideoFaceDetect(TemplateView):
    template_name = 'video.html'

    def post(self, request, *args, **kwargs):
        return JsonResponse(status=200, data={'message': 'Face detected'})



