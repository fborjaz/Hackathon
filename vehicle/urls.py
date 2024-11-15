from django.urls import path
from .views import Landing, Revision, Comparacion, ChatVehicle

urlpatterns = [
    path("", Landing, name="home"),
    path("view/", Revision, name="view"),
    path("comparacion/", Comparacion, name="comparation"),
    path('chat/', ChatVehicle.as_view(), name='chat'),
]
