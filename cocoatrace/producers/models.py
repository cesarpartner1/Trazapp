from django.db import models

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
    eudr_validation_date = models.DateTimeField(null=True)
    eudr_validated_by = models.ForeignKey('infrastructure.Personnel', on_delete=models.SET_NULL, null=True)
    eudr_justification = models.TextField(blank=True)

    # Auditoría
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Plot(models.Model):
    producer = models.ForeignKey(Producer, on_delete=models.CASCADE)
    plot_code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    area_hectares = models.DecimalField(max_digits=10, decimal_places=2)

    # Geolocalización (almacenar como GeoJSON o WKT)
    polygon_geojson = models.JSONField()  # Coordenadas del polígono
    centroid_lat = models.DecimalField(max_digits=10, decimal_places=7)
    centroid_lon = models.DecimalField(max_digits=10, decimal_places=7)

    # Estado (hereda del productor pero puede tener validación adicional)
    is_active = models.BooleanField(default=True)
    eudr_compliant = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
