from django.urls import path,include
from . import views


urlpatterns = [
    path("",views.homePage,name="home"),
    path("decoding",views.decoding,name="decode"),
    path("create_encode",views.create_encode,name="decode")
]
