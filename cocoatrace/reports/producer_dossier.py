from __future__ import annotations

from datetime import datetime
from io import BytesIO

from compliance.models import EUDRStatusHistory
from eudr.models import EudrDiligenceProducer
from inventory.models import Batch
from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from surveys.models import Survey


def _format_date(value, fmt: str = "%d %b %Y") -> str:
    if not value:
        return "-"
    if isinstance(value, str):
        return value
    return value.strftime(fmt)


def _format_decimal(value) -> str:
    if value is None:
        return "-"
    return f"{value:,.2f}"


def _build_table(data, col_widths=None):
    table = Table(data, colWidths=col_widths, hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f4f6fb")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#111827")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#d1d5db")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return table


def _build_section_title(text, styles):
    return Paragraph(text, styles["SectionTitle"])


def _collect_surveys(producer):
    return (
        Survey.objects.select_related("plot", "enumerator")
        .filter(producer=producer)
        .order_by("-census_date")[:5]
    )


def _collect_batches(producer):
    return (
        Batch.objects.select_related("plot", "warehouse_location")
        .filter(producer=producer)
        .order_by("-created_at")[:5]
    )


def _collect_status_history(producer):
    return (
        EUDRStatusHistory.objects.select_related("changed_by")
        .filter(producer=producer)
        .order_by("-changed_at")[:5]
    )


def _collect_diligences(producer):
    return (
        EudrDiligenceProducer.objects.select_related("diligence")
        .filter(producer=producer)
        .order_by("-added_at")[:5]
    )


def build_producer_dossier(producer) -> bytes:
    """Generate a PDF dossier summarizing a producer's traceability."""

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=LETTER,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
        topMargin=0.85 * inch,
        bottomMargin=0.85 * inch,
    )

    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="SmallMeta",
            parent=styles["Normal"],
            fontSize=9,
            textColor=colors.HexColor("#4b5563"),
        )
    )
    styles.add(
        ParagraphStyle(
            name="SectionTitle",
            parent=styles["Heading2"],
            textColor=colors.HexColor("#111827"),
            spaceAfter=6,
        )
    )

    story = []

    story.append(Paragraph("Dossier del productor", styles["Heading1"]))
    story.append(Paragraph(f"Generado: {_format_date(datetime.now(), '%d %b %Y %H:%M')}", styles["SmallMeta"]))
    story.append(Spacer(1, 0.2 * inch))

    summary_data = [
        ["Campo", "Valor"],
        ["Nombre", producer.full_name],
        ["Código", producer.code],
        ["Documento", f"{producer.document_type} · {producer.document_number}"],
        ["Ubicación", f"{producer.municipality}, {producer.department}"],
        ["Teléfono", producer.phone],
        ["Correo", producer.email or "-"],
        ["Estado cumplimiento", producer.get_compliance_status_display()],
    ]
    story.append(_build_section_title("Resumen de identidad", styles))
    story.append(_build_table(summary_data, col_widths=[2.2 * inch, 3.8 * inch]))
    story.append(Spacer(1, 0.2 * inch))

    plots = list(producer.plot_set.all().order_by("name"))
    plot_rows = [["Parcela", "Código", "Área (ha)", "Cumple EUDR"]]
    for plot in plots:
        plot_rows.append(
            [
                plot.name,
                plot.plot_code,
                _format_decimal(plot.area_hectares),
                "Sí" if plot.eudr_compliant else "Pendiente",
            ]
        )
    if len(plot_rows) == 1:
        plot_rows.append(["Sin registros", "-", "-", "-"])
    story.append(_build_section_title("Parcelas registradas", styles))
    story.append(_build_table(plot_rows))
    story.append(Spacer(1, 0.2 * inch))

    surveys = list(_collect_surveys(producer))
    survey_rows = [["Global ID", "Parcela", "Fecha", "Enumerador", "Riesgo"]]
    for survey in surveys:
        survey_rows.append(
            [
                survey.global_id,
                survey.plot.name,
                _format_date(survey.census_date),
                getattr(survey.enumerator, "full_name", survey.enumerator) or "-",
                survey.risk_eudr or "Sin dato",
            ]
        )
    if len(survey_rows) == 1:
        survey_rows.append(["Sin encuestas", "-", "-", "-", "-"])
    story.append(_build_section_title("Encuestas recientes", styles))
    story.append(_build_table(survey_rows))
    story.append(Spacer(1, 0.2 * inch))

    batches = list(_collect_batches(producer))
    batch_rows = [["Lote", "Fecha", "Cantidad (kg)", "Parcela", "Estado"],]
    for batch in batches:
        batch_rows.append(
            [
                batch.batch_id,
                _format_date(batch.created_at),
                _format_decimal(batch.quantity),
                batch.plot.name if batch.plot_id else "-",
                dict(batch._meta.get_field("eudr_compliance_status").choices).get(batch.eudr_compliance_status, batch.eudr_compliance_status),
            ]
        )
    if len(batch_rows) == 1:
        batch_rows.append(["Sin movimientos", "-", "-", "-", "-"])
    story.append(_build_section_title("Movimientos de inventario", styles))
    story.append(_build_table(batch_rows))
    story.append(PageBreak())

    history = list(_collect_status_history(producer))
    history_rows = [["Fecha", "Estado anterior", "Nuevo estado", "Justificación"]]
    for entry in history:
        history_rows.append(
            [
                _format_date(entry.changed_at),
                entry.previous_status,
                entry.new_status,
                entry.justification[:120] + ("…" if len(entry.justification) > 120 else ""),
            ]
        )
    if len(history_rows) == 1:
        history_rows.append(["Sin eventos", "-", "-", "-"])
    story.append(_build_section_title("Historial de cumplimiento", styles))
    story.append(_build_table(history_rows))
    story.append(Spacer(1, 0.2 * inch))

    diligence_links = list(_collect_diligences(producer))
    diligence_rows = [["Diligencia", "Rol", "Estado", "Último evento"]]
    for link in diligence_links:
        diligence = link.diligence
        last_event = diligence.timeline_entries.order_by("-event_date").first()
        diligence_rows.append(
            [
                f"{diligence.reference_code} · {diligence.name}",
                link.get_role_display(),
                diligence.get_status_display(),
                _format_date(last_event.event_date) if last_event else "Sin registros",
            ]
        )
    if len(diligence_rows) == 1:
        diligence_rows.append(["Sin diligencias", "-", "-", "-"])
    story.append(_build_section_title("Participación en diligencias EUDR", styles))
    story.append(_build_table(diligence_rows))

    def _header_footer(canvas, _doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#6b7280"))
        canvas.drawString(0.75 * inch, 0.5 * inch, f"Productor {producer.code} · {producer.full_name}")
        canvas.drawRightString(7.75 * inch, 0.5 * inch, f"Página {canvas.getPageNumber()}")
        canvas.restoreState()

    doc.build(story, onFirstPage=_header_footer, onLaterPages=_header_footer)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf
