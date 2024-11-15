from django.urls import path
from .views import Landing, Revision, Comparacion

urlpatterns = [
    path("", Landing, name="home"),
    path("view/", Revision, name="view"),
    path("comparacion/", Comparacion, name="comparation"),
]
