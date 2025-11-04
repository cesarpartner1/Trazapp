from django.contrib.auth.models import AbstractUser
from django.db import models

class Personnel(AbstractUser):
    employee_id = models.CharField(max_length=50, unique=True)
    role = models.CharField(
        max_length=50,
        choices=[
            ('admin', 'Administrador'),
            ('field_operator', 'Operador de Campo'),
            ('logistics_operator', 'Operador de Logística'),
            ('compliance_manager', 'Gestor de Cumplimiento')
        ]
    )
    phone = models.CharField(max_length=20)
    is_active_employee = models.BooleanField(default=True)

class Warehouse(models.Model):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    address = models.TextField()
    municipality = models.CharField(max_length=100)
    capacity_kg = models.DecimalField(max_digits=12, decimal_places=2)
    current_stock_kg = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # Geolocalización del almacén
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True)

    is_active = models.BooleanField(default=True)

class Vehicle(models.Model):
    plate_number = models.CharField(max_length=20, unique=True)
    vehicle_type = models.CharField(max_length=50)
    capacity_kg = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
