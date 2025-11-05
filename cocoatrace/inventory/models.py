from django.db import models
from producers.models import Producer, Plot
from infrastructure.models import Warehouse

class Batch(models.Model):
    batch_id = models.CharField(max_length=100, unique=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    warehouse_location = models.ForeignKey(Warehouse, on_delete=models.SET_NULL, null=True, blank=True)
    eudr_compliance_status = models.CharField(
        max_length=20,
        choices=[('compliant', 'Conforme'), ('pending', 'Pendiente'), ('non_compliant', 'No conforme')],
        default='pending'
    )
    producer = models.ForeignKey(Producer, on_delete=models.PROTECT)
    plot = models.ForeignKey(Plot, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
