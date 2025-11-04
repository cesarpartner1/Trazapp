from django import forms

from .models import Warehouse


class WarehouseForm(forms.ModelForm):
    class Meta:
        model = Warehouse
        fields = [
            "code",
            "name",
            "address",
            "municipality",
            "capacity_kg",
            "current_stock_kg",
            "latitude",
            "longitude",
            "is_active",
        ]
        widgets = {
            "code": forms.TextInput(attrs={"class": "form-control"}),
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "address": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "municipality": forms.TextInput(attrs={"class": "form-control"}),
            "capacity_kg": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "current_stock_kg": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "latitude": forms.NumberInput(attrs={"class": "form-control", "step": "0.0000001"}),
            "longitude": forms.NumberInput(attrs={"class": "form-control", "step": "0.0000001"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
