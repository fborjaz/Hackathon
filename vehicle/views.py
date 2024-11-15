from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from vehicle.models import Vehicle
from vehicle.utils.VehicleAnalytics import VehicleDataAnalytics
from django.utils.decorators import method_decorator
import json
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
def Landing(request):
    return render(request, "landing.html")


def Revision(request):
    
    vehicles = Vehicle.objects.all()
    
    context ={
        "vehicles": vehicles
    }
    
    
    return render(request, "revision.html", context=context)


def Comparacion(request):
    return render(request, "comparacion.html")

@method_decorator(csrf_exempt, name="dispatch")
class ChatVehicle(View):
    analytics = VehicleDataAnalytics()

    def get(self, request, *args, **kwargs):
        
        makes = Vehicle.objects.values('make').distinct()
        
        context = {
            'makes': makes
        }
        
        return render(request, 'chat.html',context=context)

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        type_analytics= data.get('type_analytics')
        if type_analytics == "predict_co2_emissions":
            print(data.get('engine_size'))
            engine_size = int(data.get('engine_size'))
            cylinders = int(data.get('cylinders'))
            fuel_consumption_comb = float(data.get('fuel_consumption_comb'))
            response = self.analytics.predict_co2_emissions(engine_size, cylinders, fuel_consumption_comb)
            print(response)
            return JsonResponse(response)
        elif type_analytics == "classify_efficiency":
            engine_size = int(data.get('engine_size'))
            fuel_consumption_comb = float(data.get('fuel_consumption_comb'))
            response = self.analytics.classify_efficiency(engine_size, fuel_consumption_comb)
            print(response)
            return JsonResponse(response)
        elif type_analytics == "analyze_make_co2_trends":
            make = data.get('make')
            response = self.analytics.analyze_make_co2_trends(make)
            print(response)
            return JsonResponse(response)
        
