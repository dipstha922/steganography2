from .models import Uploads,Decoding
from django.forms import ModelForm,widgets
from django import forms

class encryptionForm(ModelForm):
    class Meta:
        model = Uploads
        fields = ["files","types","messages"]
        widgets = {
            'files' : forms.FileInput( attrs={"class" : "form-control "}),
            "messages": forms.TextInput( attrs={"class": "messages-field","placeholder":"Enter your secret message"})
            
        }


class decryptionForm(ModelForm):
    class Meta:
        model = Decoding
        fields = "__all__"