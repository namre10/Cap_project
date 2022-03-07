from unicodedata import name
from django.contrib import admin
from django.urls import path, include
from . import views


urlpatterns = [
    path('doc_signin',views.doc_signin, name="doctor_signin"),
    path('doc_signup',views.doc_register, name="doctor_signup"),
    path('activate/<uidb64>/<token>', views.activate, name="activate")
  
] 
