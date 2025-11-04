from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from infrastructure.models import Warehouse
from producers.models import Producer, Plot

from .models import Batch

def batch_list(request):
    batches = Batch.objects.all()
    return render(request, 'inventory/batch_list.html', {'batches': batches})

def create_batch(request):
    if request.method == 'POST':
        producer = get_object_or_404(Producer, pk=request.POST.get('producer'))
        plot = get_object_or_404(Plot, pk=request.POST.get('plot'), producer=producer)
        try:
            quantity = Decimal(request.POST.get('quantity'))
        except (TypeError, InvalidOperation):
            messages.error(request, 'Provide a valid quantity value. Use numbers only.')
        else:
            Batch.objects.create(
                producer=producer,
                plot=plot,
                batch_id=request.POST.get('batch_id'),
                quantity=quantity,
                warehouse_location_id=request.POST.get('warehouse_location') or None,
                eudr_compliance_status=request.POST.get('eudr_compliance_status'),
            )
            messages.success(request, 'Batch registered successfully.')
            return redirect('batch_list')

    producers = Producer.objects.all()
    warehouses = Warehouse.objects.all()
    return render(
        request,
        'inventory/create_batch.html',
        {
            'producers': producers,
            'warehouses': warehouses,
        },
    )

def get_producer_plots(request):
    producer_id = request.GET.get('producer_id')
    plots = Plot.objects.filter(producer_id=producer_id).values('id', 'name')
    return JsonResponse(list(plots), safe=False)
