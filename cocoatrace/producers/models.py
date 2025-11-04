from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
import json

def validate_geojson(value):
    """
    Validator to ensure the JSONField contains valid GeoJSON.
    """
    try:
        if not isinstance(value, dict):
            raise ValidationError("Invalid GeoJSON: must be a dictionary.")

        geom_type = value.get("type")
        coordinates = value.get("coordinates")

        if not geom_type or not coordinates:
            raise ValidationError("Invalid GeoJSON: 'type' and 'coordinates' are required.")

        if geom_type not in ["Polygon", "MultiPolygon"]:
             raise ValidationError("Invalid GeoJSON type: must be 'Polygon' or 'MultiPolygon'.")

        if not isinstance(coordinates, list):
            raise ValidationError("Invalid GeoJSON: 'coordinates' must be a list.")

        if geom_type == "Polygon":
            if not all(isinstance(ring, list) for ring in coordinates):
                raise ValidationError("Invalid Polygon: coordinates must be a list of rings.")
            if not all(isinstance(point, list) and len(point) >= 2 for ring in coordinates for point in ring):
                 raise ValidationError("Invalid Polygon: each ring must be a list of points (lists of numbers).")

    except (ValueError, TypeError):
        raise ValidationError("Invalid GeoJSON format.")


class Producer(models.Model):
    # Identificación
    code = models.CharField(max_length=50, unique=True)
    full_name = models.CharField(max_length=200)
    document_type = models.CharField(max_length=20)
    document_number = models.CharField(max_length=50)

    # Contacto y ubicación
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    address = models.TextField()
    municipality = models.CharField(max_length=100)
    department = models.CharField(max_length=100)

    # Estado EUDR
    eudr_status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pendiente'), ('validated', 'Validado'), ('rejected', 'Rechazado')],
        default='pending'
    )
    eudr_validation_date = models.DateTimeField(null=True, blank=True)
    eudr_validated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    eudr_justification = models.TextField(blank=True)

    # Auditoría
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Plot(models.Model):
    producer = models.ForeignKey(Producer, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    plot_code = models.CharField(max_length=50, unique=True)
    area_hectares = models.DecimalField(max_digits=10, decimal_places=2)

    # Geolocalización
    polygon = models.JSONField(validators=[validate_geojson], null=True, blank=True)

    # Estado (hereda del productor pero puede tener validación adicional)
    is_active = models.BooleanField(default=True)
    eudr_compliant = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
