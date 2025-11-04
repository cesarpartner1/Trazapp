from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Batch
from producers.models import Producer, Plot

def batch_list(request):
    batches = Batch.objects.all()
    return render(request, 'inventory/batch_list.html', {'batches': batches})

def create_batch(request):
    if request.method == 'POST':
        producer = Producer.objects.get(pk=request.POST.get('producer'))
        plot = Plot.objects.get(pk=request.POST.get('plot'))
        Batch.objects.create(
            producer=producer,
            plot=plot,
            batch_id=request.POST.get('batch_id'),
            quantity=request.POST.get('quantity'),
            warehouse_location_id=request.POST.get('warehouse_location'),
            eudr_compliance_status=request.POST.get('eudr_compliance_status')
        )
        return redirect('batch_list')
    producers = Producer.objects.all()
    warehouses = Warehouse.objects.all()
    return render(request, 'inventory/create_batch.html', {'producers': producers, 'warehouses': warehouses})

def get_producer_plots(request):
    producer_id = request.GET.get('producer_id')
    plots = Plot.objects.filter(producer_id=producer_id).values('id', 'name')
    return JsonResponse(list(plots), safe=False)
