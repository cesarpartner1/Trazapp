from django import forms


class FeatureCollectionUploadForm(forms.Form):
    geojson_file = forms.FileField(
        label="Archivo GeoJSON",
        help_text="Sube un archivo .json o .geojson con un FeatureCollection de polígonos.",
        widget=forms.ClearableFileInput(attrs={"class": "form-control"}),
    )

    def clean_geojson_file(self):
        uploaded = self.cleaned_data["geojson_file"]
        if uploaded.size == 0:
            raise forms.ValidationError("El archivo está vacío.")
        if uploaded.size > 5 * 1024 * 1024:
            raise forms.ValidationError("El archivo excede el límite de 5 MB.")
        return uploaded
