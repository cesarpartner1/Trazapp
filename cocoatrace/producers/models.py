from django.db import models
from django.core.exceptions import ValidationError


def _ensure_closed_ring(ring):
    if not ring:
        return ring
    first = ring[0]
    last = ring[-1]
    if first[0] == last[0] and first[1] == last[1]:
        return ring
    return ring + [first]


def _ring_centroid(ring):
    closed = _ensure_closed_ring(ring)
    if len(closed) < 4:  # minimum three vertices + closing point
        xs = [point[0] for point in closed]
        ys = [point[1] for point in closed]
        if not xs or not ys:
            return None, None, 0
        return sum(xs) / len(xs), sum(ys) / len(ys), 0

    twice_area = 0
    cx = 0
    cy = 0
    for idx in range(len(closed) - 1):
        x0, y0 = closed[idx]
        x1, y1 = closed[idx + 1]
        cross = (x0 * y1) - (x1 * y0)
        twice_area += cross
        cx += (x0 + x1) * cross
        cy += (y0 + y1) * cross

    if twice_area == 0:
        xs = [point[0] for point in closed[:-1]]
        ys = [point[1] for point in closed[:-1]]
        return sum(xs) / len(xs), sum(ys) / len(ys), 0

    area = twice_area / 2.0
    return cx / (3 * twice_area), cy / (3 * twice_area), abs(area)


def compute_centroid(geometry):
    geom_type = geometry.get("type")
    coordinates = geometry.get("coordinates")

    if geom_type == "Polygon":
        lon, lat, area = _ring_centroid(coordinates[0])
        if lon is None or lat is None:
            return None
        return lat, lon

    if geom_type == "MultiPolygon":
        total_area = 0
        sum_lat = 0
        sum_lon = 0
        for polygon in coordinates:
            lon, lat, area = _ring_centroid(polygon[0])
            if lon is None or lat is None:
                continue
            total_area += area
            sum_lat += lat * area
            sum_lon += lon * area
        if total_area:
            return sum_lat / total_area, sum_lon / total_area
        # fall back to first polygon centroid if areas cancel out
        if coordinates:
            lon, lat, _ = _ring_centroid(coordinates[0][0])
            if lon is not None and lat is not None:
                return lat, lon
        return None

    return None

def validate_geojson(value):
    """
    Validator to ensure the JSONField contains valid GeoJSON.
    """
    try:
        if not isinstance(value, dict):
            raise ValidationError("GeoJSON inválido: debe ser un diccionario.")

        geom_type = value.get("type")
        coordinates = value.get("coordinates")

        if not geom_type or not coordinates:
            raise ValidationError("GeoJSON inválido: los campos 'type' y 'coordinates' son obligatorios.")

        if geom_type not in ["Polygon", "MultiPolygon"]:
            raise ValidationError("Tipo de GeoJSON inválido: debe ser 'Polygon' o 'MultiPolygon'.")

        if not isinstance(coordinates, list):
            raise ValidationError("GeoJSON inválido: 'coordinates' debe ser una lista.")

        if geom_type == "Polygon":
            if not all(isinstance(ring, list) for ring in coordinates):
                raise ValidationError("Polígono inválido: las coordenadas deben ser una lista de anillos.")
            if not all(isinstance(point, list) and len(point) >= 2 for ring in coordinates for point in ring):
                raise ValidationError("Polígono inválido: cada anillo debe ser una lista de puntos (listas numéricas).")

    except (ValueError, TypeError):
        raise ValidationError("Formato de GeoJSON inválido.")


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

    # Compliance
    compliance_status = models.CharField(
        max_length=20,
        choices=[('Approved', 'Aprobado'), ('Pending Review', 'Pendiente por revisar'), ('Rejected', 'Rechazado')],
        default='Pending Review'
    )

    # Auditoría
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Document(models.Model):
    producer = models.ForeignKey(Producer, on_delete=models.CASCADE, related_name='documents')
    name = models.CharField(max_length=200)
    file = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

class Plot(models.Model):
    producer = models.ForeignKey(Producer, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    plot_code = models.CharField(max_length=50, unique=True)
    area_hectares = models.DecimalField(max_digits=10, decimal_places=2)

    # Geolocalización
    polygon = models.JSONField(
        validators=[validate_geojson],
        null=True,
        blank=True,
        db_column="polygon_geojson",
    )
    centroid_lat = models.FloatField(default=0)
    centroid_lng = models.FloatField(default=0, db_column="centroid_lon")

    # Estado (hereda del productor pero puede tener validación adicional)
    is_active = models.BooleanField(default=True)
    eudr_compliant = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        centroid = compute_centroid(self.polygon) if self.polygon else None
        if centroid:
            self.centroid_lat, self.centroid_lng = centroid
        else:
            self.centroid_lat = self.centroid_lat or 0
            self.centroid_lng = self.centroid_lng or 0
        super().save(*args, **kwargs)
