from asyncio.log import logger
from unittest import result
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login
from main import settings
from django.core.mail import EmailMessage, send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from . tokens import generate_token

from .models import GeneralData

from .forms import GeneralDataForm

# Create your views here.
def home(request):
    return render(request, "welcome_page/w_index.html")


from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def signin(request):
    
    if request.method == "POST":
        username = request.POST['username']
        pass1 = request.POST['pass1']

        user = authenticate(username=username, password=pass1)

        if user is not None:
            login(request, user)
            fname = user.first_name
            return render(request,'patient/general.html', {'fname':fname})

        else:
            messages.error(request, "Wrong Username/password")


    return render(request, "authentication_patient/login.html")


def signup(request):

    if request.method == "POST":

        #username = request.POST.get(username)
        username = request.POST['username']
        fname = request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']

        if User.objects.filter(username=username):
            messages.error(request, "Username Already Exist! Please try some other username")
            return redirect('patient_login')

        if User.objects.filter(email=email):
             messages.error(request, "Email already registered!")
             return redirect('patient_login')

        if len(username)>10:
            messages.error(request, 'Username must not exceed 10 characters')

        if pass1!=pass2:
            messages.error(request, 'Password did not match')

        if not username.isalnum():
            messages.error(request, 'username must be alphanumeric')
            return redirect('patient_login')


        myuser = User.objects.create_user(username,email,pass1)
        myuser.first_name = fname
        myuser.last_name = lname
        myuser.is_active = False
        myuser.save()

        print(myuser)

        messages.success(request, "Your account has been Successfully Created.\n"+ "Confirmation email has been sent\n"+"Please confirm your email in order to activate your account")


        #WELCOME EMAIL
        subject = "WELCOME TO OUR PORTAL"
        message = "HELLO" + myuser.first_name + "!! \n" + "We have sent you a confirmation email, please confirm your email address"
        from_email = settings.EMAIL_HOST_USER
        to_list = [myuser.email]
        send_mail(subject, message, from_email, to_list, fail_silently=True)

        #EMAIL ADDRESS CONFIRMATION EMAIL
        current_site = get_current_site(request)
        email_subject = "Confirm your email "
        message2 = render_to_string('email_confirmation.html' ,{
            'name': myuser.first_name,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(myuser.pk)),
            'token': generate_token.make_token(myuser)
        })

        email = EmailMessage(
            email_subject,
            message2,
            settings.EMAIL_HOST_USER,
            [myuser.email],
        )
        email.fail_silently = True
        email.send()

        return redirect('patient_login') 

    return render(request, "authentication_patient/signup.html")

def logout(request):
    pass


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        myuser = User.objects.get(pk=uid)
    except (TypeError , ValueError, OverflowError, User.DoesNotExist):
        myuser = None
    
    if myuser is not None and generate_token.check_token(myuser, token):
        myuser.is_active = True
        myuser.save()
        login(request, myuser)
        context = {'uidb64':uidb64, 'token':token}
        return redirect('patient_login', context)
    else:
        return render(request, 'activation_failed.html')



def General(request):
    data = GeneralData.objects.all()

    if request.method == 'POST':
        form = GeneralDataForm(request.POST)
        if form.is_valid():
            form.save()
    else:
        form = GeneralDataForm()
    context ={
        'data': data,
        'form': form,
    }

    return render(request, 'patient/General.html', context)


def patientinfo(request):
    return render(request,'patient/view_profile.html')

def editinfo(request):
    return render(request, 'patient/edit_profile.html')

def Hospitals(request):
    return render(request, 'patient/hospitals.html')




## Disease Prediction


from .forms import ImageUploadForm

import io
import os
import base64  

import torch.nn as nn
import torch.nn.functional as F

from torchvision import transforms
import torch 
from PIL import Image
from django.conf import settings


class Covid_Normal_CNN(nn.Module):
    
    def __init__(self):
        super(Covid_Normal_CNN, self).__init__()
        
        self.layer1 = nn.Sequential(
            nn.Conv2d(in_channels=1, out_channels=16, kernel_size=1, padding=1),
            nn.BatchNorm2d(16),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2)
        )
        
        self.layer2 = nn.Sequential(
            nn.Conv2d(in_channels=16, out_channels=32, kernel_size=1),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.MaxPool2d(2)
        )
        
        self.fc1 = nn.Linear(in_features=80000, out_features=600)
        self.drop = nn.Dropout2d(0.25)
        self.fc2 = nn.Linear(in_features=600, out_features=120)
        self.fc3 = nn.Linear(in_features=120, out_features=1)
        self.sigmoid = nn.Sigmoid()
        
    def forward(self, x):
        out = self.layer1(x)
        out = self.layer2(out)
        out = out.view(out.size(0), -1)
        out = self.fc1(out)
        out = self.drop(out)
        out = self.fc2(out)
        out = self.fc3(out)
        out = self.sigmoid(out)
        
        return out

model = Covid_Normal_CNN()
model.load_state_dict(torch.load('resnet50_best.pth', map_location='cpu'))

def transform_image(image_bytes):
    my_transforms = transforms.Compose([
        transforms.RandomCrop(200),
        transforms.ToTensor(),
        transforms.Normalize((0),(1))
    ])

    image = Image.open(io.BytesIO(image_bytes))
    image = image.resize((200, 200))
    image = my_transforms(image).unsqueeze(dim=0)

    return image


def get_prediction(image_bytes):
    tensor = transform_image(image_bytes)
    prediction = model(tensor)
    
    if(prediction <= 0.50):
        predicted_idx = "COVID"
    else:
        predicted_idx = "NORMAL"
    
    return predicted_idx

def disease_prediction(request):
    image_uri = None
    predicted_label = None

    if request.method == 'POST':
        # in case of POST: get the uploaded image from the form and process it
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # retrieve the uploaded image and convert it to bytes (for PyTorch)
            image = form.cleaned_data['image']
            image_bytes = image.file.read()
            # convert and pass the image as base64 string to avoid storing it to DB or filesystem
            encoded_img = base64.b64encode(image_bytes).decode('ascii')
            image_uri = 'data:%s;base64,%s' % ('image/png', encoded_img)

            # get predicted label with previously implemented PyTorch function
            try:
                predicted_label = get_prediction(image_bytes)
            except RuntimeError as re:
                print(re)

    else:
        # in case of GET: simply show the empty form for uploading images
        form = ImageUploadForm()

    # pass the form, image URI, and predicted label to the template to be rendered
    context = {
        'form': form,
        'image_uri': image_uri,
        'predicted_label': predicted_label,
    }
    return render(request, 'patient/disease_prediction.html', context)

# def Disease_Prediction(request):
#     return render(request, 'disease_prediction/disease_prediction.html')