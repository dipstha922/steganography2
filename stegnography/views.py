from django.shortcuts import render,redirect
from django.http import HttpResponse
from .forms import encryptionForm,decryptionForm
from .models import Uploads
from .utils import waveAudioEncrypt,waveAudioDecrypt,midiAudioDecrypt,midiAudioEncrypt


def decoding(request):

    if request.method == "POST" and request.FILES["filename"]:

        myfile = request.FILES["filename"]
        names  = myfile.name
        ext = names.split(".")

        if ext[-1]=="wav":
            message = waveAudioDecrypt(myfile)
            
            content = {
                "message" : message,
                "get_message":"has_message"
            }

            return render(request,"decode.html",content)

        elif ext[-1] =="mid":
            message = midiAudioDecrypt(myfile)

            content = {
                "message" : message,
                "get_message" : "has_message"
            }

            return render(request,"decode.html",content)

        else:

            content = {
                
                "get_message":"dont_have"
            }

            return render(request,"decode.html",content)


    else:

     

        return render(request,"decode.html")
    

def create_encode(request):

    if request.method == "POST":
        message = request.POST.get("message_midi")
       
        uploading = Uploads.objects.create(types="midi")
        # second create the file
       
        midiAudioEncrypt(message,uploading.uniqueIds) # create along with encode 
        # third link the file created to uploaded file
        uploading.files = "/midi/{}.mid".format(uploading.uniqueIds)
        uploading.messages = message
        uploading.save()
        download  = Uploads.objects.get(uniqueIds=uploading.uniqueIds)
        
        content = {
            "downloadLink":uploading.uniqueIds,
            "file":"midi"
        }
        return render(request,"downloadpage.html",content)

    else:
        return render(request,"create.html")





def homePage(request):
    
    if request.method == 'POST':
    
        forms = encryptionForm(request.POST,request.FILES)
  
        if forms.is_valid():
            saving = forms.save(commit=False)
            messages = forms.cleaned_data["messages"]
            files = forms.cleaned_data["files"]
            ext = files.name
            ext = ext.split(".")
            if ext[-1] == "wav":
                uploading= Uploads.objects.create(types="wave")
                waveAudioEncrypt(files,messages,uploading.uniqueIds)
                uploading.files = "/media/documents/{}.wav".format(uploading.uniqueIds)
                uploading.messages = messages
                uploading.save()
                
                content ={
                    "downloadLink":uploading.uniqueIds,
                    "file":"wave"
                }
                return render(request,"downloadpage.html",content)
            else:
                return redirect("/")


        else:
            # output file not matched type 
            return redirect('/')
            
    else:

        encryptionForms = encryptionForm()
        
        content = {
            "encryptionForms":encryptionForms
           
        }

        return render(request,"index.html",content)



