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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = getattr(self, "instance", None)
        if not self.is_bound and instance and instance.pk and instance.polygon:
            initial_value = self.initial.get("polygon", instance.polygon)
            if not isinstance(initial_value, str):
                json_value = json.dumps(instance.polygon)
                self.initial["polygon"] = json_value
                self.fields["polygon"].initial = json_value

    def clean_polygon(self):
        raw_value = self.cleaned_data["polygon"]
        if not raw_value:
            raise forms.ValidationError("Dibuja el límite de la parcela en el mapa antes de guardar.")
        try:
            parsed = json.loads(raw_value)
        except json.JSONDecodeError as exc:
            raise forms.ValidationError("El GeoJSON proporcionado no es válido.") from exc
        centroid = compute_centroid(parsed)
        if not centroid:
            raise forms.ValidationError("No fue posible calcular el centroide de la geometría proporcionada.")
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
