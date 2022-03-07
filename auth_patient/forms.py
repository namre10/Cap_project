from django import forms
from .models import GeneralData

class GeneralDataForm(forms.ModelForm):
    class Meta:
        model = GeneralData
        fields = ('water_consumption', 'calories_burnt')
        widget = {
            'waterconsumption': forms.IntegerField(widget=forms.FileInput(attrs={'class':'general-form'})),
            'calories_burnt': forms.IntegerField(widget=forms.FileInput(attrs={'class':'general-form'})),
        }

class ImageUploadForm(forms.Form):
    image = forms.ImageField()