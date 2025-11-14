import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone

from inventory.models import Batch
from producers.models import Producer


def eudr_upload_to(instance, filename):
    return f"eudr/{timezone.now():%Y/%m}/{instance.diligence_id}/{filename}"


class EudrDiligence(models.Model):
    STATUS_CHOICES = [
        ("draft", "Borrador"),
        ("active", "En curso"),
        ("completed", "Completada"),
        ("archived", "Archivada"),
    ]

    id = models.BigAutoField(primary_key=True)
    public_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=255)
    reference_code = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    target_market = models.CharField(max_length=120, blank=True)
    opened_at = models.DateField(default=timezone.now)
    closed_at = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    producers = models.ManyToManyField(
        Producer,
        through="EudrDiligenceProducer",
        related_name="eudr_diligences",
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Diligencia EUDR"
        verbose_name_plural = "Diligencias EUDR"

    def __str__(self):
        return f"{self.reference_code} · {self.name}"


class EudrDiligenceProducer(models.Model):
    ROLE_CHOICES = [
        ("supplier", "Proveedor"),
        ("buyer", "Comprador"),
        ("origin", "Origen"),
    ]

    diligence = models.ForeignKey(EudrDiligence, on_delete=models.CASCADE)
    producer = models.ForeignKey(Producer, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="supplier")
    notes = models.CharField(max_length=255, blank=True)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("diligence", "producer")
        verbose_name = "Participante de diligencia"
        verbose_name_plural = "Participantes de diligencia"

    def __str__(self):
        return f"{self.producer} en {self.diligence}"


class EudrTimelineEntry(models.Model):
    EVENT_TYPES = [
        ("reception_note", "Nota de recepción"),
        ("delivery_note", "Nota de entrega"),
        ("sales_invoice", "Factura de venta"),
        ("due_diligence", "Debida diligencia"),
        ("custom", "Evento personalizado"),
    ]

    STATUS_CHOICES = [
        ("pending", "Pendiente"),
        ("approved", "Aprobado"),
        ("rejected", "Rechazado"),
    ]

    diligence = models.ForeignKey(
        EudrDiligence,
        on_delete=models.CASCADE,
        related_name="timeline_entries",
    )
    event_type = models.CharField(max_length=40, choices=EVENT_TYPES)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    event_date = models.DateField(default=timezone.now)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="eudr_entries",
    )
    batch = models.ForeignKey(Batch, null=True, blank=True, on_delete=models.SET_NULL)
    meta = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-event_date", "-created_at"]
        verbose_name = "Evento de diligencia"
        verbose_name_plural = "Eventos de diligencia"

    def __str__(self):
        return f"{self.get_event_type_display()} · {self.event_date:%Y-%m-%d}"


class EudrDocument(models.Model):
    DOCUMENT_TYPES = [
        ("reception_note", "Nota de recepción"),
        ("delivery_note", "Nota de entrega"),
        ("sales_invoice", "Factura de venta"),
        ("due_diligence", "Debida diligencia"),
        ("other", "Otro"),
    ]

    diligence = models.ForeignKey(
        EudrDiligence,
        on_delete=models.CASCADE,
        related_name="documents",
    )
    timeline_entry = models.ForeignKey(
        EudrTimelineEntry,
        on_delete=models.CASCADE,
        related_name="documents",
        null=True,
        blank=True,
    )
    document_type = models.CharField(max_length=40, choices=DOCUMENT_TYPES)
    file = models.FileField(upload_to=eudr_upload_to)
    original_name = models.CharField(max_length=255)
    mime_type = models.CharField(max_length=120, blank=True)
    file_size = models.PositiveIntegerField(default=0)
    notes = models.CharField(max_length=255, blank=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="eudr_documents",
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-uploaded_at"]
        verbose_name = "Documento EUDR"
        verbose_name_plural = "Documentos EUDR"

    def __str__(self):
        return self.original_name or self.file.name