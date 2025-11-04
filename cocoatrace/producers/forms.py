import json

from django import forms

from .models import Document, Plot, Producer, compute_centroid


class ProducerForm(forms.ModelForm):
    class Meta:
        model = Producer
        fields = [
            "full_name",
            "code",
            "document_type",
            "document_number",
            "phone",
            "email",
            "address",
            "municipality",
            "department",
            "compliance_status",
        ]
        widgets = {
            "full_name": forms.TextInput(attrs={"class": "form-control"}),
            "code": forms.TextInput(attrs={"class": "form-control"}),
            "document_type": forms.TextInput(attrs={"class": "form-control"}),
            "document_number": forms.TextInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "address": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "municipality": forms.TextInput(attrs={"class": "form-control"}),
            "department": forms.TextInput(attrs={"class": "form-control"}),
            "compliance_status": forms.Select(attrs={"class": "form-select"}),
        }


class PlotForm(forms.ModelForm):
    polygon = forms.CharField(widget=forms.HiddenInput())

    class Meta:
        model = Plot
        fields = ["name", "plot_code", "area_hectares", "polygon"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "plot_code": forms.TextInput(attrs={"class": "form-control"}),
            "area_hectares": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
        }

    def clean_polygon(self):
        raw_value = self.cleaned_data["polygon"]
        if not raw_value:
            raise forms.ValidationError("Draw the plot boundary on the map before saving.")
        try:
            parsed = json.loads(raw_value)
        except json.JSONDecodeError as exc:
            raise forms.ValidationError("Invalid GeoJSON payload.") from exc
        centroid = compute_centroid(parsed)
        if not centroid:
            raise forms.ValidationError("Unable to compute a centroid for the provided geometry.")
        self.cleaned_data["centroid_values"] = centroid
        return parsed

    def save(self, commit=True):
        instance = super().save(commit=False)
        centroid = self.cleaned_data.get("centroid_values")
        if centroid:
            instance.centroid_lat, instance.centroid_lng = centroid
        if commit:
            instance.save()
            self.save_m2m()
        return instance


class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ["name", "file"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "file": forms.FileInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["file"].required = False
