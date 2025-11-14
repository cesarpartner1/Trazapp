import json
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Any, Dict, Iterable, Optional

from django.db import transaction
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.utils.text import slugify

from core.models import ActivityLog
from core.utils import log_activity
from producers.models import Plot, Producer

from .models import Enumerator, Survey


@dataclass
class ImportSummary:
    producers_created: int = 0
    producers_updated: int = 0
    plots_created: int = 0
    plots_updated: int = 0
    surveys_created: int = 0
    surveys_updated: int = 0
    errors: list[str] = None

    def __post_init__(self) -> None:
        if self.errors is None:
            self.errors = []

    def as_dict(self) -> Dict[str, Any]:
        return {
            "producers_created": self.producers_created,
            "producers_updated": self.producers_updated,
            "plots_created": self.plots_created,
            "plots_updated": self.plots_updated,
            "surveys_created": self.surveys_created,
            "surveys_updated": self.surveys_updated,
            "errors": self.errors,
        }


def _clean_string(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (int, float, Decimal)):
        return str(value).strip()
    return str(value).strip()


def _normalize_identifier(value: Any) -> str:
    text = _clean_string(value)
    if text.endswith(".0"):
        text = text[:-2]
    return text


def _decimal_or_none(value: Any) -> Optional[Decimal]:
    if value in (None, ""):
        return None
    if isinstance(value, Decimal):
        return value
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return None


def _decimal_or_zero(value: Any) -> Decimal:
    decimal_value = _decimal_or_none(value)
    return decimal_value if decimal_value is not None else Decimal("0")


def _int_or_none(value: Any) -> Optional[int]:
    if value in (None, ""):
        return None
    try:
        if isinstance(value, bool):
            return int(value)
        if isinstance(value, (int, Decimal)):
            return int(value)
        float_value = float(str(value))
        return int(round(float_value))
    except (ValueError, TypeError):
        return None


def _parse_datetime(value: Any) -> Optional[datetime]:
    if not value:
        return None
    if isinstance(value, datetime):
        return timezone.make_aware(value, timezone.get_current_timezone()) if timezone.is_naive(value) else value
    text = _clean_string(value)
    if not text:
        return None
    # Reemplazamos el sufijo Z por +00:00 para compatibilidad con parse_datetime
    parsed = parse_datetime(text.replace("Z", "+00:00"))
    return parsed


def _ensure_polygon(geometry: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(geometry, dict):
        raise ValueError("La geometría no es un objeto válido.")
    geom_type = geometry.get("type")
    if geom_type not in {"Polygon", "MultiPolygon"}:
        raise ValueError("Solo se admiten geometrías Polygon o MultiPolygon.")
    return geometry


def _unique_plot_code(base: str, existing_codes: set[str]) -> str:
    candidate = base
    suffix = 1
    while candidate in existing_codes:
        suffix += 1
        candidate = f"{base}-{suffix}"
    existing_codes.add(candidate)
    return candidate


def import_feature_collection(data: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(data, dict):
        raise ValueError("El archivo no contiene un objeto JSON válido.")
    if data.get("type") != "FeatureCollection":
        raise ValueError("Solo se admiten archivos GeoJSON con type=FeatureCollection.")

    features: Iterable[Dict[str, Any]] = data.get("features") or []
    if not isinstance(features, Iterable):
        raise ValueError("El FeatureCollection no incluye una lista de features.")

    summary = ImportSummary()
    existing_plot_codes = set(Plot.objects.values_list("plot_code", flat=True))

    for index, feature in enumerate(features, start=1):
        try:
            _process_feature(feature, summary, existing_plot_codes)
        except Exception as exc:  # pylint: disable=broad-except
            summary.errors.append(f"Feature {index}: {exc}")

    return summary.as_dict()


@transaction.atomic
def _process_feature(feature: Dict[str, Any], summary: ImportSummary, existing_plot_codes: set[str]) -> None:
    if not isinstance(feature, dict):
        raise ValueError("El feature no es un objeto JSON válido.")

    properties = feature.get("properties") or {}
    geometry = _ensure_polygon(feature.get("geometry"))

    global_id = _normalize_identifier(properties.get("globalid")) or _normalize_identifier(properties.get("globalId"))
    if not global_id:
        raise ValueError("El feature no incluye el identificador 'globalid'.")

    producer = _get_or_create_producer(properties, summary)
    plot = _get_or_create_plot(properties, geometry, producer, global_id, summary, existing_plot_codes)
    enumerator = _get_or_create_enumerator(properties)
    _create_or_update_survey(properties, global_id, producer, plot, enumerator, summary)


def _get_or_create_producer(properties: Dict[str, Any], summary: ImportSummary) -> Producer:
    document_number = _normalize_identifier(properties.get("CI_RIF_Productor"))
    producer_name = _clean_string(properties.get("Nombre_Productor")) or "Productor sin nombre"
    producer_code = _clean_string(properties.get("ID_UP")) or document_number or f"PR-{slugify(producer_name) or 'sin-codigo'}"
    producer_code = producer_code.strip() or f"PR-{document_number or slugify(producer_name) or 'sin-codigo'}"
    if producer_code in {"", "None"}:
        producer_code = f"PR-{timezone.now().strftime('%Y%m%d%H%M%S')}"

    producer = None
    if document_number:
        producer = Producer.objects.filter(document_number=document_number).first()
    if not producer:
        producer = Producer.objects.filter(code=producer_code).first()

    defaults = {
        "code": producer_code,
        "full_name": producer_name,
        "document_type": _clean_string(properties.get("document_type") or "CI"),
        "document_number": document_number or producer_code,
        "phone": _clean_string(properties.get("Telef_Productor")),
        "email": "",
        "address": "",
        "municipality": _clean_string(properties.get("municipio")),
        "department": _clean_string(properties.get("departamento")),
        "sector": _clean_string(properties.get("sector_unidad_producion")),
        "community": _clean_string(properties.get("comunidad_unidad_producion")),
        "notes": _clean_string(properties.get("observaciones_encuestador")),
    }

    if producer:
        updated = False
        for field, value in defaults.items():
            if value and getattr(producer, field) != value:
                setattr(producer, field, value)
                updated = True
        if updated:
            producer.save()
            summary.producers_updated += 1
            log_activity("Productor", f"Datos actualizados: {producer.full_name}", producer.code, event_type=ActivityLog.EVENT_UPDATE)
    else:
        producer = Producer.objects.create(**defaults)
        summary.producers_created += 1
        log_activity("Productor", f"Nuevo productor importado: {producer.full_name}", producer.code, event_type=ActivityLog.EVENT_CREATE)

    return producer


def _get_or_create_plot(
    properties: Dict[str, Any],
    geometry: Dict[str, Any],
    producer: Producer,
    global_id: str,
    summary: ImportSummary,
    existing_plot_codes: set[str],
) -> Plot:
    plot = Plot.objects.filter(global_id=global_id).first()

    area_total = _decimal_or_zero(properties.get("Sup_UP_ha"))
    cocoa_area = _decimal_or_none(properties.get("Sup_Cacao_UP"))

    plot_name = _clean_string(properties.get("ID_UP")) or f"Parcela {producer.code}"
    plot_code_base = slugify(_clean_string(properties.get("ID_UP")) or producer.code or global_id) or global_id.lower()
    plot_code = plot.plot_code if plot else _unique_plot_code(plot_code_base.upper(), existing_plot_codes)

    plot_values = {
        "producer": producer,
        "name": plot_name,
        "plot_code": plot_code,
        "global_id": global_id,
        "area_hectares": area_total,
        "reported_area_ha": area_total if area_total else None,
        "polygon": geometry,
        "eudr_compliant": False,
    }
    if cocoa_area is not None:
        plot_values["reported_area_ha"] = cocoa_area

    if plot:
        changed = False
        for field, value in plot_values.items():
            if getattr(plot, field) != value:
                setattr(plot, field, value)
                changed = True
        if changed:
            plot.save()
            summary.plots_updated += 1
            log_activity("Parcela", f"Parcela actualizada: {plot.name}", producer.code, event_type=ActivityLog.EVENT_UPDATE)
    else:
        plot = Plot.objects.create(**plot_values)
        summary.plots_created += 1
        log_activity("Parcela", f"Parcela importada: {plot.name}", producer.code, event_type=ActivityLog.EVENT_CREATE)

    return plot


def _get_or_create_enumerator(properties: Dict[str, Any]) -> Optional[Enumerator]:
    enumerator_id = _normalize_identifier(properties.get("ID_Encuestador"))
    if not enumerator_id:
        return None
    enumerator, _ = Enumerator.objects.get_or_create(document_number=enumerator_id)
    return enumerator


def _create_or_update_survey(
    properties: Dict[str, Any],
    global_id: str,
    producer: Producer,
    plot: Plot,
    enumerator: Optional[Enumerator],
    summary: ImportSummary,
) -> None:
    survey_defaults = {
        "producer": producer,
        "plot": plot,
        "enumerator": enumerator,
        "census_date": _parse_datetime(properties.get("Data_Censo")) or timezone.now(),
        "creation_date": _parse_datetime(properties.get("CreationDate")),
        "edit_date": _parse_datetime(properties.get("EditDate")),
        "reported_area_ha": _decimal_or_none(properties.get("Sup_UP_ha")),
        "cocoa_area_ha": _decimal_or_none(properties.get("Sup_Cacao_UP")),
        "buyer": _clean_string(properties.get("A_quien_arrima")),
        "crops": _clean_string(properties.get("_qu_rubros_cultivan_en_la_unida")),
        "other_crop": _clean_string(properties.get("otro_rubro")),
        "insai_registered": _clean_string(properties.get("_esta_inscrito_en_el_insai_sige")),
        "has_rubber": _clean_string(properties.get("_posee_plantas_de_caucho_en_la")),
        "training_received": _clean_string(properties.get("_ha_recibido_formaci_n_para_mej")),
        "varieties": _clean_string(properties.get("_qu_variedades_de_cacao_tiene_c")),
        "plant_origin": _clean_string(properties.get("_cu_l_es_el_origen_de_su_planta")),
        "other_origin": _clean_string(properties.get("otro_origen")),
        "cultural_practices": _clean_string(properties.get("practicas_culturales")),
        "other_practice": _clean_string(properties.get("otra_practica")),
        "fertilizers": _clean_string(properties.get("_cu_les_fertilizantes_utilizan")),
        "pesticides": _clean_string(properties.get("_cu_les_pesticidas_usan_para_el")),
        "pest_issues": _clean_string(properties.get("_que_problemas_con_plagas_insec")),
        "harvest_volume": _int_or_none(properties.get("_aproximadamente_qu_cantidad_de")),
        "cocoa_plants": _int_or_none(properties.get("cantidad_plantas_cacao")),
        "plant_spacing": _clean_string(properties.get("distancia_plantas")),
        "families_supported": _int_or_none(properties.get("familias_que_dependen_UP")),
        "seniors": _int_or_none(properties.get("Adultos_mayores_de_60")),
        "adults": _int_or_none(properties.get("Adultos_entre_18_a_60")),
        "teens": _int_or_none(properties.get("Adolescentes_entre_13_17")),
        "children": _int_or_none(properties.get("Nino_menores_de_13")),
        "female_total": _int_or_none(properties.get("Total_de_hembras_Familia")),
        "male_total": _int_or_none(properties.get("Total_varones_en_Familia")),
        "highest_education": _clean_string(properties.get("_cu_l_es_el_mayor_nivel_de_educ")),
        "workers_total": _int_or_none(properties.get("Trabajadores_en_UP")),
        "workers_men": _int_or_none(properties.get("Trabajadores_hombres_UP")),
        "workers_women": _int_or_none(properties.get("Trabajadores_mujeres_UP")),
        "workers_teens": _int_or_none(properties.get("Trabajadores_adolecen_UP")),
        "workers_children": _int_or_none(properties.get("Trabajadores_ninos_UP")),
        "health_condition": _clean_string(properties.get("_alg_n_integrante_de_la_unidad")),
        "other_disease": _clean_string(properties.get("otra_enfermedad")),
        "observations": _clean_string(properties.get("observaciones_encuestador")),
        "risk_eudr": _clean_string(properties.get("riesgo_EDUR")),
        "raw_properties": json.loads(json.dumps(properties)),
    }

    survey, created = Survey.objects.update_or_create(
        global_id=global_id,
        defaults=survey_defaults,
    )
    if created:
        summary.surveys_created += 1
        log_activity("Encuesta", f"Encuesta importada: {plot.name}", producer.code, event_type=ActivityLog.EVENT_CREATE)
    else:
        summary.surveys_updated += 1
        log_activity("Encuesta", f"Encuesta actualizada: {plot.name}", producer.code, event_type=ActivityLog.EVENT_UPDATE)