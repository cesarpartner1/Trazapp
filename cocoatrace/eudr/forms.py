from django import forms

from inventory.models import Batch
from producers.models import Producer

from .models import EudrDiligence, EudrTimelineEntry


class EudrDiligenceForm(forms.ModelForm):
    producers = forms.ModelMultipleChoiceField(
        queryset=Producer.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={"class": "form-select", "size": 6}),
        label="Productores vinculados",
    )

    class Meta:
        model = EudrDiligence
        fields = [
            "name",
            "reference_code",
            "description",
            "target_market",
            "status",
            "opened_at",
            "closed_at",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "reference_code": forms.TextInput(attrs={"class": "form-control"}),
            "target_market": forms.TextInput(attrs={"class": "form-control"}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "opened_at": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "closed_at": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "description": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
        }

    def save(self, commit=True):
        diligence = super().save(commit=commit)
        producers = self.cleaned_data.get("producers")
        if commit and producers is not None:
            diligence.producers.set(producers)
        return diligence


class EudrAttachProducerForm(forms.Form):
    producers = forms.ModelMultipleChoiceField(
        queryset=Producer.objects.all(),
        widget=forms.SelectMultiple(attrs={"class": "form-select", "size": 8}),
        label="Selecciona productores",
    )
    role = forms.ChoiceField(
        choices=[("supplier", "Proveedor"), ("buyer", "Comprador"), ("origin", "Origen")],
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    notes = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Notas opcionales"}),
    )


class EudrTimelineEntryForm(forms.ModelForm):
    document_file = forms.FileField(
        required=False,
        label="Documento adjunto",
        widget=forms.ClearableFileInput(attrs={"class": "form-control"}),
    )
    document_notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 2, "class": "form-control"}),
        label="Notas del documento",
    )
    batch = forms.ModelChoiceField(
        queryset=Batch.objects.all(),
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
        label="Vincular lote (Nota de entrega)",
    )

    class Meta:
        model = EudrTimelineEntry
        fields = [
            "event_type",
            "title",
            "description",
            "status",
            "event_date",
            "batch",
        ]
        widgets = {
            "event_type": forms.Select(attrs={"class": "form-select"}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "event_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "title": forms.TextInput(attrs={"class": "form-control"}),
        }

    def clean(self):
        cleaned = super().clean()
        event_type = cleaned.get("event_type")
        batch = cleaned.get("batch")
        if event_type == "delivery_note" and not batch:
            self.add_error("batch", "Selecciona el lote asociado a la nota de entrega.")
        return cleaned
