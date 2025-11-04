import json

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

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
        Document.objects.create(
            producer=producer,
            name=request.POST.get('name'),
            file=request.FILES.get('file'),
        )
        messages.success(request, 'Document uploaded.')
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
            messages.success(request, 'Plot added to producer profile.')
            return redirect('producer_detail', pk=producer_pk)
        messages.error(request, 'Fix the highlighted issues and try again.')

    return render(
        request,
        'producers/add_plot.html',
        {
            'producer': producer,
            'form': form,
        },
    )


def create_producer(request):
    form = ProducerForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            producer = form.save()
            messages.success(request, 'Producer profile created.')
            return redirect('producer_detail', pk=producer.pk)
        messages.error(request, 'Review the form and resolve validation errors.')

    return render(
        request,
        'producers/create_producer.html',
        {
            'form': form,
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
            messages.success(request, 'Document updated successfully.')
            return redirect('producer_detail', pk=producer_pk)
        messages.error(request, 'Resolve the errors below and try again.')

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
        document.delete()
        messages.success(request, 'Document removed.')
        return redirect('producer_detail', pk=producer_pk)

    return render(
        request,
        'producers/delete_document.html',
        {
            'producer': producer,
            'document': document,
        },
    )
