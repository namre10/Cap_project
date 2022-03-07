from unicodedata import name
from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('',views.home, name="home"),
    path('signin',views.signin, name="patient_login"),
    path('signup',views.signup, name="patient_signup"),
    path('activate/<uidb64>/<token>', views.activate, name="activate"),

    # ALL SIDEBAR CONTENTS
    path('General', views.General, name="General"),
    path('Patient_info', views.patientinfo, name="Patient_info"),
    path('Edit_profile', views.editinfo, name="Edit_profile"),
    path('Hospitals', views.Hospitals, name="Hospitals"),  


    # Path for disease prediction 
    path('disease_prediction', views.disease_prediction, name='disease_prediction'),

]
