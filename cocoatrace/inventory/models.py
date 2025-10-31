from django.db import models

class Batch(models.Model):
    # Identificación única
    batch_id = models.CharField(max_length=100, unique=True)
    batch_type = models.CharField(max_length=50)  # 'field', 'consolidated', etc.

    # Origen EUDR (clave para trazabilidad)
    origin_plot = models.ForeignKey('producers.Plot', on_delete=models.PROTECT)
    origin_producer = models.ForeignKey('producers.Producer', on_delete=models.PROTECT)

    # Características del lote
    weight_kg = models.DecimalField(max_digits=10, decimal_places=2)
    quality_grade = models.CharField(max_length=50, blank=True)

    # Estado EUDR (heredado del productor/parcela)
    eudr_status = models.CharField(
        max_length=20,
        choices=[('eligible', 'Apto'), ('pending', 'Pendiente'), ('non_compliant', 'No Conforme')]
    )

    # Ubicación actual y estado
    current_location = models.ForeignKey('infrastructure.Warehouse', on_delete=models.SET_NULL, null=True)
    status = models.CharField(
        max_length=20,
        choices=[('in_field', 'En Finca'), ('in_transit', 'En Tránsito'), ('in_warehouse', 'En Almacén'), ('consolidated', 'Consolidado')]
    )

    # Consolidación (si es lote maestro)
    is_consolidated = models.BooleanField(default=False)
    parent_batch = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)

    created_at = models.DateTimeField(auto_now_add=True)

class Movement(models.Model):
    movement_id = models.CharField(max_length=100, unique=True)
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)

    # Origen y destino
    origin_type = models.CharField(max_length=20)  # 'farm', 'warehouse'
    origin_location = models.ForeignKey('infrastructure.Warehouse', related_name='movements_out', on_delete=models.SET_NULL, null=True)
    destination_location = models.ForeignKey('infrastructure.Warehouse', related_name='movements_in', on_delete=models.PROTECT)

    # Transporte
    vehicle = models.ForeignKey('infrastructure.Vehicle', on_delete=models.SET_NULL, null=True)
    driver = models.ForeignKey('infrastructure.Personnel', on_delete=models.SET_NULL, null=True)

    # Estado y fechas
    status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pendiente'), ('in_transit', 'En Tránsito'), ('received', 'Recibido'), ('cancelled', 'Cancelado')]
    )
    dispatch_date = models.DateTimeField()
    received_date = models.DateTimeField(null=True)
    received_by = models.ForeignKey('infrastructure.Personnel', related_name='received_movements', on_delete=models.SET_NULL, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
