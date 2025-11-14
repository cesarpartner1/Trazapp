from django.contrib import admin

from .models import EudrDiligence, EudrDiligenceProducer, EudrTimelineEntry, EudrDocument


class EudrDocumentInline(admin.TabularInline):
    model = EudrDocument
    extra = 0
    fields = ("document_type", "file", "uploaded_by", "uploaded_at")
    readonly_fields = ("uploaded_at",)


class EudrTimelineEntryInline(admin.TabularInline):
    model = EudrTimelineEntry
    extra = 0
    fields = ("event_type", "title", "event_date", "status")


@admin.register(EudrDiligence)
class EudrDiligenceAdmin(admin.ModelAdmin):
    list_display = ("reference_code", "name", "status", "opened_at", "created_at")
    list_filter = ("status", "opened_at")
    search_fields = ("reference_code", "name")
    inlines = [EudrTimelineEntryInline]


@admin.register(EudrTimelineEntry)
class EudrTimelineEntryAdmin(admin.ModelAdmin):
    list_display = ("diligence", "event_type", "status", "event_date", "created_at")
    list_filter = ("event_type", "status", "event_date")
    search_fields = ("title", "description", "diligence__reference_code")
    inlines = [EudrDocumentInline]


@admin.register(EudrDocument)
class EudrDocumentAdmin(admin.ModelAdmin):
    list_display = ("original_name", "document_type", "diligence", "uploaded_by", "uploaded_at")
    list_filter = ("document_type", "uploaded_at")
    search_fields = ("original_name", "notes", "diligence__reference_code")


@admin.register(EudrDiligenceProducer)
class EudrDiligenceProducerAdmin(admin.ModelAdmin):
    list_display = ("diligence", "producer", "role", "added_at")
    list_filter = ("role",)
    search_fields = ("diligence__reference_code", "producer__full_name")
