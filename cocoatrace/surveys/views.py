import json

from django.contrib import messages
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from .forms import FeatureCollectionUploadForm
from .services import import_feature_collection


@require_http_methods(["GET", "POST"])
def import_geojson(request):
    summary = None
    form = FeatureCollectionUploadForm(request.POST or None, request.FILES or None)

    if request.method == "POST" and form.is_valid():
        uploaded = form.cleaned_data["geojson_file"]
        try:
            payload = json.load(uploaded)
        except json.JSONDecodeError:
            form.add_error("geojson_file", "El archivo no contiene JSON válido.")
        else:
            summary = import_feature_collection(payload)
            if summary["errors"]:
                messages.warning(request, f"Importación completada con {len(summary['errors'])} errores.")
            else:
                messages.success(request, "Importación completada correctamente.")
            form = FeatureCollectionUploadForm()

    return render(
        request,
        "surveys/import_geojson.html",
        {
            "form": form,
            "summary": summary,
        },
    )
