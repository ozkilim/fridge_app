import datetime
import re
import json
import pytz
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.http import HttpResponse, request
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from foodscan.middleware.login_exempt import login_exempt
from foodshow.forms import CustomUserCreationForm, CustomFoodsForm, CustomFridgeFoodsForm
from foodshow.models import Fridge, FoodData, CustomUser
from foodshow.ocr_core import ocr_core
from foodshow.tokens import account_activation_token
import cv2
from pyzbar import pyzbar

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
            print(user)
            # passwrd check here.... how is the page rendering password areas if its not in the form..
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

            return HttpResponse(
                'Please confirm your email address to complete the registration')  # should redirect to dead end page until user confirms email
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

def fridge_filler(response, extracted_text):
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
        food = Fridge(used=False, fooddata_id=i)
        food.save()

    return redirect('foodshow:index')




def index(request):
    fridge_foods = Fridge.objects.all()
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
                days_left = "Today"
            elif days_left == 1:
                days_left = "Tomorrow"
            fridge_food_id = one_food.id

            food_list.append({"foodname": foodname, "scanneddate": scanneddate, "days_left": days_left,
                              "fridge_food_id": fridge_food_id, "food_image": food_image})

    day_list = ["Today", "Tomorrow", 2, 3, 4, 5, 6, 7, 8, "over 8 days"]
    return render(request, "index.html", {"food_list": food_list, "day_list": day_list})


def sort_by_catagory(request):
    fridge_foods = Fridge.objects.all()
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

            print(str(extracted_text))
            print("here is the food!")
            # extract the text and display it
            # then make user say yes or no.../correct the text...?
            # text correction/edits could take place here


            return redirect('foodshow:fridge_filler', extracted_text=str(extracted_text))

    elif request.method == 'GET':
        return render(request, 'upload.html')


def eaten(request):
    if request.method == 'POST' :
        if 'submit' in request.POST:
            non_eaten_food_id = request.POST.get('submit')
            get_eaten_food_from_fridge = Fridge.objects.get(id=non_eaten_food_id)
            get_eaten_food_from_fridge.used = False
            get_eaten_food_from_fridge.save()

        elif 'delete_foods' in request.POST:
            Fridge.objects.filter(used=True).delete()

    fridge_foods = Fridge.objects.all()
    eaten_foods = []
    for one_food in fridge_foods:
        get_food_id = int(one_food.fooddata_id)
        foodname = FoodData.objects.get(id=get_food_id).food_name
        fridge_food_id = one_food.id
        food_image = FoodData.objects.get(id=get_food_id).image_of_food
        if one_food.used == True:
            eaten_foods.append({"foodname": foodname, "fridge_food_id": fridge_food_id, "food_image": food_image})

    return render(request, 'eaten.html', {"eaten_foods": eaten_foods})


class VideoCamera(object):
    def __init__(self):
        # Using OpenCV to capture from device 0. If you have trouble capturing
        # from a webcam, comment the line below out and use a video file
        # instead.
        self.video = cv2.VideoCapture(0)
        # If you decide to use video.mp4, you must have this file in the folder
        # as the main.py.
        # self.video = cv2.VideoCapture('video.mp4')

    def __del__(self):
        self.video.release()

    def get_frame(self):
        success, image = self.video.read()
        # We are using Motion JPEG, but OpenCV defaults to capture raw images,
        # so we must encode it into JPEG in order to correctly display the
        # video stream.

        # _, frame = cap.read()
        decodedObjects = pyzbar.decode(image)
        thedata = None
        for obj in decodedObjects:
            print("Data", obj.data)
            # this is the print...
            thedata = obj.data
        ret, jpeg = cv2.imencode('.jpg', image)

        return jpeg.tobytes(), thedata


def gen(camera):
    while True:
        frame = camera.get_frame()[0]
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        if camera.get_frame()[1] is not None:
            break

    return shopping()


def shopping(request):
    return render(request, 'shopping.html')


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
            form.save()
            print("saved")
            return render(request, "custom_foods.html")
    else:
        form = CustomFoodsForm()
    # payment_to = scanner.camera()
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
        form = CustomFridgeFoodsForm(request.POST)
        with open('customfoods.txt') as json_file:
            context = json.load(json_file)
        food_added_list = context["food_added_list"]
        if form.is_valid():
            x = form.save()
            foodid =x.fooddata_id
            thisfood = FoodData.objects.get(id=foodid).food_name
            food_added_list.append(thisfood)
            data = {"food_added_list":food_added_list}
            print(data)
            with open('customfoods.txt', 'w') as outfile:
                json.dump(data, outfile)
        return redirect("foodshow:fridge_manager")
    else:
        with open('customfoods.txt') as json_file:
            context = json.load(json_file)
        passinlist = context["food_added_list"]
        form = CustomFridgeFoodsForm()

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
