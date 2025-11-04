from django.shortcuts import render, get_object_or_404, redirect
from .models import Producer, Plot, Document
import json

def producer_list(request):
    producers = Producer.objects.all()
    return render(request, 'producers/producer_list.html', {'producers': producers})

def producer_detail(request, pk):
    producer = get_object_or_404(Producer, pk=pk)
    plots = Plot.objects.filter(producer=producer)

    if request.method == 'POST':
        Document.objects.create(
            producer=producer,
            name=request.POST.get('name'),
            file=request.FILES.get('file')
        )
        return redirect('producer_detail', pk=pk)

    return render(request, 'producers/producer_detail.html', {'producer': producer, 'plots': plots})

def add_plot(request, producer_pk):
    producer = get_object_or_404(Producer, pk=producer_pk)
    if request.method == 'POST':
        polygon_str = request.POST.get('polygon')
        if polygon_str:
            polygon_data = json.loads(polygon_str)
            Plot.objects.create(
                producer=producer,
                name=request.POST.get('name'),
                plot_code=request.POST.get('plot_code'),
                area_hectares=request.POST.get('area_hectares'),
                polygon=polygon_data
            )
            return redirect('producer_detail', pk=producer_pk)
    return render(request, 'producers/add_plot.html', {'producer': producer})
