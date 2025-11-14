import json

from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.utils.http import url_has_allowed_host_and_scheme

from .forms import FeatureCollectionUploadForm
from .services import import_feature_collection
from .models import Survey


def survey_list(request):
    query = request.GET.get("q", "").strip()
    surveys = Survey.objects.select_related("producer", "plot", "enumerator").all()

    if query:
        surveys = surveys.filter(
            Q(producer__full_name__icontains=query)
            | Q(producer__code__icontains=query)
            | Q(plot__name__icontains=query)
            | Q(global_id__icontains=query)
        )

    paginator = Paginator(surveys, 25)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "surveys/survey_list.html",
        {
            "page_obj": page_obj,
            "surveys": page_obj.object_list,
            "query": query,
            "total_count": paginator.count,
        },
    )


def survey_detail(request, pk):
    survey = get_object_or_404(
        Survey.objects.select_related("producer", "plot", "enumerator"),
        pk=pk,
    )
    return_url = request.GET.get("next")
    if return_url and not url_has_allowed_host_and_scheme(
        return_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return_url = None
    sections = [
        (
            "Identificación",
            {
                "Productor": survey.producer.full_name,
                "Código productor": survey.producer.code,
                "Parcela": survey.plot.name,
                "Global ID": survey.global_id,
                "Fecha censo": survey.census_date,
                "Encuestador": survey.enumerator,
            },
        ),
        (
            "Áreas y cultivos",
            {
                "Área reportada (ha)": survey.reported_area_ha,
                "Área cacao (ha)": survey.cocoa_area_ha,
                "Cultivos": survey.crops,
                "Otra especie": survey.other_crop,
                "Variedades": survey.varieties,
                "Origen plantas": survey.plant_origin,
                "Otra procedencia": survey.other_origin,
            },
        ),
        (
            "Prácticas y sanidad",
            {
                "Registro INSAI": survey.insai_registered,
                "Tiene caucho": survey.has_rubber,
                "Capacitaciones": survey.training_received,
                "Prácticas culturales": survey.cultural_practices,
                "Otra práctica": survey.other_practice,
                "Fertilizantes": survey.fertilizers,
                "Plaguicidas": survey.pesticides,
                "Problemas de plagas": survey.pest_issues,
            },
        ),
        (
            "Producción",
            {
                "Volumen cosecha": survey.harvest_volume,
                "Plantas de cacao": survey.cocoa_plants,
                "Distancia siembra": survey.plant_spacing,
                "Comprador": survey.buyer,
            },
        ),
        (
            "Composición familiar",
            {
                "Familias atendidas": survey.families_supported,
                "Adultos mayores": survey.seniors,
                "Adultos": survey.adults,
                "Adolescentes": survey.teens,
                "Niños": survey.children,
                "Mujeres": survey.female_total,
                "Hombres": survey.male_total,
                "Educación": survey.highest_education,
            },
        ),
        (
            "Mano de obra",
            {
                "Total trabajadores": survey.workers_total,
                "Hombres": survey.workers_men,
                "Mujeres": survey.workers_women,
                "Adolescentes": survey.workers_teens,
                "Niños": survey.workers_children,
            },
        ),
        (
            "Salud y observaciones",
            {
                "Condición de salud": survey.health_condition,
                "Otra enfermedad": survey.other_disease,
                "Observaciones": survey.observations,
                "Riesgo EUDR": survey.risk_eudr,
            },
        ),
    ]

    return render(
        request,
        "surveys/survey_detail.html",
        {
            "survey": survey,
            "sections": sections,
            "return_url": return_url,
        },
    )


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
