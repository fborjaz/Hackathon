from django.db import models
class Vehicle(models.Model):
    make = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    year_of_manufacture = models.IntegerField()
    vehicle_class = models.CharField(max_length=100)
    engine_size = models.DecimalField(max_digits=4, decimal_places=2)
    cylinders = models.IntegerField()
    transmission = models.CharField(max_length=100)
    fuel_type = models.CharField(max_length=50)
    fuel_consumption_city = models.DecimalField(max_digits=5, decimal_places=2)
    fuel_consumption_hwy = models.DecimalField(max_digits=5, decimal_places=2)
    fuel_consumption_comb = models.DecimalField(max_digits=5, decimal_places=2)
    fuel_consumption_comb_mpg = models.DecimalField(max_digits=5, decimal_places=2)
    co2_emissions = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f"{self.make} {self.model} ({self.year_of_manufacture})"
