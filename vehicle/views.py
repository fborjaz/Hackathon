from django.shortcuts import render


# Create your views here.
def Landing(request):
    return render(request, "landing.html")


def Revision(request):
    return render(request, "revision.html")


def Comparacion(request):
    return render(request, "comparacion.html")
