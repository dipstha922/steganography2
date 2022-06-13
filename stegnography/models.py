from django.db import models
# from .utils import encryption,encry
import wave
import uuid


# # Create your models here.
class Decoding(models.Model):

    choises=(
        ("midi","MIDI"),
        ("wave","WAVE")
    )
    files = models.FileField(upload_to="documents/decoding/")
    types =  models.CharField(max_length=10,choices=choises,blank=True,default=False)


class Uploads(models.Model):

    choises=(
        ("midi","MIDI"),
        ("wave","WAVE")
    )
    files = models.FileField(upload_to='documents/')
    types = models.CharField(max_length=20,choices=choises,blank=True,default="wave")
    messages= models.TextField(max_length=100,blank=True)
    uniqueIds= models.UUIDField(default=uuid.uuid1,editable=False,blank=True)
    
    def __str__(self):
        return self.types
