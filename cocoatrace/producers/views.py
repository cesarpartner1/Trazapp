import json

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from core.models import ActivityLog
from core.utils import log_activity
from .forms import DocumentForm, PlotForm, ProducerForm
from .models import Document, Plot, Producer


def producer_list(request):
    producers = Producer.objects.prefetch_related('plot_set')
    return render(request, 'producers/producer_list.html', {'producers': producers})


def producer_detail(request, pk):
    producer = get_object_or_404(
        Producer.objects.prefetch_related('plot_set', 'documents'),
        pk=pk,
    )
    plots = producer.plot_set.all()
    plot_features = []
    for plot in plots:
        geometry = plot.polygon
        if isinstance(geometry, str) and geometry:
            try:
                geometry = json.loads(geometry)
            except json.JSONDecodeError:
                geometry = None

        plot_features.append(
            {
                'id': plot.pk,
                'name': plot.name,
                'code': plot.plot_code,
                'area': float(plot.area_hectares),
                'geometry': geometry,
                'centroid': {
                    'lat': plot.centroid_lat,
                    'lng': plot.centroid_lng,
                },
            }
        )

    if request.method == 'POST':
        document = Document.objects.create(
            producer=producer,
            name=request.POST.get('name'),
            file=request.FILES.get('file'),
        )
        log_activity('Documento', f"Documento cargado: {document.name}", producer.full_name, event_type=ActivityLog.EVENT_CREATE)
        messages.success(request, 'Documento cargado.')
        return redirect('producer_detail', pk=pk)

    return render(
        request,
        'producers/producer_detail.html',
        {
            'producer': producer,
            'plots': plots,
            'plot_features': plot_features,
        },
    )


def add_plot(request, producer_pk):
    producer = get_object_or_404(Producer, pk=producer_pk)
    form = PlotForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            plot = form.save(commit=False)
            plot.producer = producer
            plot.save()
            log_activity('Parcela', f"Parcela agregada: {plot.name}", producer.full_name, event_type=ActivityLog.EVENT_CREATE)
            messages.success(request, 'Parcela agregada al perfil del productor.')
            return redirect('producer_detail', pk=producer_pk)
        messages.error(request, 'Corrige los campos marcados e intenta de nuevo.')

    return render(
        request,
        'producers/add_plot.html',
        {
            'producer': producer,
            'form': form,
            'page_title': 'Nueva parcela',
            'page_helper': 'Dibuja el límite de la finca y captura los datos agronómicos clave.',
            'cancel_url': reverse('producer_detail', args=[producer.pk]),
            'submit_label': 'Guardar parcela',
            'is_edit': False,
        },
    )


def edit_plot(request, producer_pk, plot_pk):
    producer = get_object_or_404(Producer, pk=producer_pk)
    plot = get_object_or_404(Plot, pk=plot_pk, producer=producer)
    form = PlotForm(request.POST or None, instance=plot)

    if request.method == 'POST':
        if form.is_valid():
            plot = form.save()
            log_activity('Parcela', f"Parcela actualizada: {plot.name}", producer.full_name, event_type=ActivityLog.EVENT_UPDATE)
            messages.success(request, 'Parcela actualizada correctamente.')
            return redirect('producer_detail', pk=producer_pk)
        messages.error(request, 'Corrige los campos marcados e intenta de nuevo.')

    return render(
        request,
        'producers/add_plot.html',
        {
            'producer': producer,
            'form': form,
            'page_title': 'Editar parcela',
            'page_helper': 'Ajusta los datos de la parcela para conservar la trazabilidad precisa.',
            'cancel_url': reverse('producer_detail', args=[producer.pk]),
            'submit_label': 'Actualizar parcela',
            'is_edit': True,
        },
    )


def create_producer(request):
    form = ProducerForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            producer = form.save()
            log_activity('Productor', f"Nuevo productor: {producer.full_name}", producer.code, event_type=ActivityLog.EVENT_CREATE)
            messages.success(request, 'Perfil de productor creado.')
            return redirect('producer_detail', pk=producer.pk)
        messages.error(request, 'Revisa el formulario y corrige los errores de validación.')

    return render(
        request,
        'producers/create_producer.html',
        {
            'form': form,
            'page_subtitle': 'Registro',
            'page_title': 'Nuevo productor',
            'page_helper': 'Captura la identidad, los datos de contacto y la información de cumplimiento del productor siguiendo los pasos para mantener la calidad del dato.',
            'cancel_url': reverse('producer_list'),
            'submit_label': 'Crear productor',
        },
    )


def edit_producer(request, pk):
    producer = get_object_or_404(Producer, pk=pk)
    form = ProducerForm(request.POST or None, instance=producer)

    if request.method == 'POST':
        if form.is_valid():
            producer = form.save()
            log_activity('Productor', f"Productor actualizado: {producer.full_name}", producer.code, event_type=ActivityLog.EVENT_UPDATE)
            messages.success(request, 'Perfil de productor actualizado.')
            return redirect('producer_detail', pk=producer.pk)
        messages.error(request, 'Revisa el formulario y corrige los errores de validación.')

    return render(
        request,
        'producers/create_producer.html',
        {
            'form': form,
            'page_subtitle': producer.code,
            'page_title': 'Editar productor',
            'page_helper': 'Actualiza la información del productor para mantener la trazabilidad al día.',
            'cancel_url': reverse('producer_detail', args=[producer.pk]),
            'submit_label': 'Guardar cambios',
            'delete_url': reverse('delete_producer', args=[producer.pk]),
            'is_edit': True,
        },
    )


def plot_detail(request, producer_pk, plot_pk):
    producer = get_object_or_404(Producer, pk=producer_pk)
    plot = get_object_or_404(Plot, pk=plot_pk, producer=producer)
    geojson = json.dumps(plot.polygon) if plot.polygon else None

    return render(
        request,
        'producers/plot_detail.html',
        {
            'producer': producer,
            'plot': plot,
            'plot_geojson': geojson,
        },
    )


def edit_document(request, producer_pk, document_pk):
    producer = get_object_or_404(Producer, pk=producer_pk)
    document = get_object_or_404(Document, pk=document_pk, producer=producer)
    form = DocumentForm(request.POST or None, request.FILES or None, instance=document)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            log_activity('Documento', f"Documento actualizado: {document.name}", producer.full_name, event_type=ActivityLog.EVENT_UPDATE)
            messages.success(request, 'Documento actualizado correctamente.')
            return redirect('producer_detail', pk=producer_pk)
        messages.error(request, 'Soluciona los errores y vuelve a intentarlo.')

    return render(
        request,
        'producers/edit_document.html',
        {
            'producer': producer,
            'document': document,
            'form': form,
        },
    )


def delete_document(request, producer_pk, document_pk):
    producer = get_object_or_404(Producer, pk=producer_pk)
    document = get_object_or_404(Document, pk=document_pk, producer=producer)

    if request.method == 'POST':
        name = document.name
        document.delete()
        log_activity('Documento', f"Documento eliminado: {name}", producer.full_name, event_type=ActivityLog.EVENT_DELETE)
        messages.success(request, 'Documento eliminado.')
        return redirect('producer_detail', pk=producer_pk)

    return render(
        request,
        'producers/delete_document.html',
        {
            'producer': producer,
            'document': document,
        },
    )


def delete_producer(request, pk):
    producer = get_object_or_404(Producer, pk=pk)

    if request.method == 'POST':
        name = producer.full_name
        code = producer.code
        producer.delete()
        log_activity('Productor', f"Productor eliminado: {name}", code, event_type=ActivityLog.EVENT_DELETE)
        messages.success(request, 'Productor eliminado correctamente.')
        return redirect('producer_list')

    return render(
        request,
        'producers/delete_producer.html',
        {
            'producer': producer,
        },
    )
