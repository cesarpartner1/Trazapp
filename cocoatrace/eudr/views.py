from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import DetailView, ListView, CreateView

from .forms import (
    EudrAttachProducerForm,
    EudrDiligenceForm,
    EudrTimelineEntryForm,
)
from .models import (
    EudrDiligence,
    EudrDiligenceProducer,
    EudrTimelineEntry,
    EudrDocument,
)


class DiligenceListView(LoginRequiredMixin, ListView):
    template_name = "eudr/dashboard.html"
    context_object_name = "diligences"
    model = EudrDiligence

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        active = self.object_list.filter(status="active").count()
        pending_docs = EudrTimelineEntry.objects.filter(status="pending").count()
        context.update(
            {
                "active_count": active,
                "pending_docs": pending_docs,
                "total_documents": EudrDocument.objects.count(),
            }
        )
        return context


class DiligenceCreateView(LoginRequiredMixin, CreateView):
    template_name = "eudr/create_diligence.html"
    form_class = EudrDiligenceForm
    success_url = reverse_lazy("eudr:diligence_list")

    def form_valid(self, form):
        messages.success(self.request, "Diligencia creada correctamente.")
        return super().form_valid(form)


class DiligenceDetailView(LoginRequiredMixin, DetailView):
    template_name = "eudr/diligence_detail.html"
    slug_field = "public_id"
    slug_url_kwarg = "public_id"
    model = EudrDiligence

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.setdefault("timeline_form", EudrTimelineEntryForm())
        context.setdefault("attach_form", EudrAttachProducerForm())
        context["timeline"] = self.object.timeline_entries.select_related("batch", "created_by").prefetch_related("documents")
        context["documents"] = self.object.documents.select_related("uploaded_by", "timeline_entry")[:10]
        return context


class TimelineEntryCreateView(LoginRequiredMixin, View):
    def post(self, request, public_id):
        diligence = get_object_or_404(EudrDiligence, public_id=public_id)
        form = EudrTimelineEntryForm(request.POST, request.FILES)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.diligence = diligence
            entry.created_by = request.user
            entry.save()
            if form.cleaned_data.get("document_file"):
                uploaded_file = form.cleaned_data["document_file"]
                doc = EudrDocument.objects.create(
                    diligence=diligence,
                    timeline_entry=entry,
                    document_type=form.cleaned_data["event_type"],
                    file=uploaded_file,
                    original_name=uploaded_file.name,
                    mime_type=getattr(uploaded_file, "content_type", ""),
                    file_size=getattr(uploaded_file, "size", 0),
                    notes=form.cleaned_data.get("document_notes", ""),
                    uploaded_by=request.user,
                )
                entry.meta = {**entry.meta, "document_id": doc.id}
                entry.save(update_fields=["meta"])
            if entry.event_type == "delivery_note" and entry.batch:
                entry.meta = {
                    **entry.meta,
                    "batch_id": entry.batch.batch_id,
                    "quantity": str(entry.batch.quantity),
                }
                entry.save(update_fields=["meta"])
            messages.success(request, "Evento agregado al timeline.")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
        return redirect("eudr:diligence_detail", public_id=public_id)


class AttachProducerView(LoginRequiredMixin, View):
    def post(self, request, public_id):
        diligence = get_object_or_404(EudrDiligence, public_id=public_id)
        form = EudrAttachProducerForm(request.POST)
        if form.is_valid():
            producers = form.cleaned_data["producers"]
            for producer in producers:
                EudrDiligenceProducer.objects.get_or_create(
                    diligence=diligence,
                    producer=producer,
                    defaults={
                        "role": form.cleaned_data["role"],
                        "notes": form.cleaned_data.get("notes", ""),
                        "added_at": timezone.now(),
                    },
                )
            messages.success(request, "Productores agregados a la diligencia.")
        else:
            messages.error(request, "No fue posible agregar los productores seleccionados.")
        return redirect("eudr:diligence_detail", public_id=public_id)
