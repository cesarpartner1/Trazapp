from django.db import models

class EUDRStatusHistory(models.Model):
    """Auditoría de cambios de estado EUDR"""
    producer = models.ForeignKey('producers.Producer', on_delete=models.CASCADE)
    previous_status = models.CharField(max_length=20)
    new_status = models.CharField(max_length=20)
    justification = models.TextField()
    changed_by = models.ForeignKey('infrastructure.Personnel', on_delete=models.PROTECT)
    changed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.producer.code} · {self.previous_status}→{self.new_status} ({self.changed_at:%Y-%m-%d})"

class DueDiligenceStatement(models.Model):
    """Declaración de Diligencia Debida EUDR"""
    statement_id = models.CharField(max_length=100, unique=True)
    batch = models.ForeignKey('inventory.Batch', on_delete=models.PROTECT)

    # Datos compilados en el momento de generación
    producer_data = models.JSONField()  # Snapshot de datos del productor
    plot_polygon = models.JSONField()  # Polígono de la parcela origen
    chain_of_custody = models.JSONField()  # Historial completo de movimientos

    # Documento generado
    pdf_file = models.FileField(upload_to='eudr_statements/')
    generated_by = models.ForeignKey('infrastructure.Personnel', on_delete=models.PROTECT)
    generated_at = models.DateTimeField(auto_now_add=True)

    # Estado
    status = models.CharField(
        max_length=20,
        choices=[('draft', 'Borrador'), ('submitted', 'Presentado'), ('approved', 'Aprobado')]
    )

    def __str__(self):
        return f"Declaración {self.statement_id} ({self.get_status_display()})"
