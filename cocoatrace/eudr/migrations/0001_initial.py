from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid

import eudr.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("producers", "0007_plot_global_id_plot_reported_area_ha_and_more"),
        ("inventory", "0004_remove_batch_eudr_status_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="EudrDiligence",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("public_id", models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ("name", models.CharField(max_length=255)),
                ("reference_code", models.CharField(max_length=100, unique=True)),
                ("description", models.TextField(blank=True)),
                ("status", models.CharField(choices=[("draft", "Borrador"), ("active", "En curso"), ("completed", "Completada"), ("archived", "Archivada")], default="draft", max_length=20)),
                ("target_market", models.CharField(blank=True, max_length=120)),
                ("opened_at", models.DateField(default=django.utils.timezone.now)),
                ("closed_at", models.DateField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "ordering": ["-created_at"],
                "verbose_name": "Diligencia EUDR",
                "verbose_name_plural": "Diligencias EUDR",
            },
        ),
        migrations.CreateModel(
            name="EudrTimelineEntry",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("event_type", models.CharField(choices=[("reception_note", "Nota de recepción"), ("delivery_note", "Nota de entrega"), ("sales_invoice", "Factura de venta"), ("due_diligence", "Debida diligencia"), ("custom", "Evento personalizado")], max_length=40)),
                ("title", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True)),
                ("status", models.CharField(choices=[("pending", "Pendiente"), ("approved", "Aprobado"), ("rejected", "Rechazado")], default="pending", max_length=20)),
                ("event_date", models.DateField(default=django.utils.timezone.now)),
                ("meta", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("batch", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="inventory.batch")),
                ("created_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="eudr_entries", to=settings.AUTH_USER_MODEL)),
                ("diligence", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="timeline_entries", to="eudr.eudrdiligence")),
            ],
            options={
                "ordering": ["-event_date", "-created_at"],
                "verbose_name": "Evento de diligencia",
                "verbose_name_plural": "Eventos de diligencia",
            },
        ),
        migrations.CreateModel(
            name="EudrDocument",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("document_type", models.CharField(choices=[("reception_note", "Nota de recepción"), ("delivery_note", "Nota de entrega"), ("sales_invoice", "Factura de venta"), ("due_diligence", "Debida diligencia"), ("other", "Otro")], max_length=40)),
                ("file", models.FileField(upload_to=eudr.models.eudr_upload_to)),
                ("original_name", models.CharField(max_length=255)),
                ("mime_type", models.CharField(blank=True, max_length=120)),
                ("file_size", models.PositiveIntegerField(default=0)),
                ("notes", models.CharField(blank=True, max_length=255)),
                ("uploaded_at", models.DateTimeField(auto_now_add=True)),
                ("diligence", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="documents", to="eudr.eudrdiligence")),
                ("timeline_entry", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="documents", to="eudr.eudrtimelineentry")),
                ("uploaded_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="eudr_documents", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ["-uploaded_at"],
                "verbose_name": "Documento EUDR",
                "verbose_name_plural": "Documentos EUDR",
            },
        ),
        migrations.CreateModel(
            name="EudrDiligenceProducer",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("role", models.CharField(choices=[("supplier", "Proveedor"), ("buyer", "Comprador"), ("origin", "Origen")], default="supplier", max_length=20)),
                ("notes", models.CharField(blank=True, max_length=255)),
                ("added_at", models.DateTimeField(auto_now_add=True)),
                ("diligence", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="eudr.eudrdiligence")),
                ("producer", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="producers.producer")),
            ],
            options={
                "verbose_name": "Participante de diligencia",
                "verbose_name_plural": "Participantes de diligencia",
                "unique_together": {("diligence", "producer")},
            },
        ),
        migrations.AddField(
            model_name="eudrdiligence",
            name="producers",
            field=models.ManyToManyField(related_name="eudr_diligences", through="eudr.EudrDiligenceProducer", to="producers.producer"),
        ),
    ]
