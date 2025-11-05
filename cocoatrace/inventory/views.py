from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.db import transaction
from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from infrastructure.models import Warehouse
from producers.models import Producer, Plot

from .models import Batch


def _recalculate_warehouse_stock(warehouse_id):
    """Actualizar el stock del almacén sumando los lotes asociados."""
    if not warehouse_id:
        return

    total = (
        Batch.objects.filter(warehouse_location_id=warehouse_id)
        .aggregate(total=Sum('quantity'))
        .get('total')
        or Decimal('0')
    )
    Warehouse.objects.filter(pk=warehouse_id).update(current_stock_kg=total)

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
            messages.error(request, 'Ingresa una cantidad válida utilizando solo números.')
        else:
            warehouse_id = request.POST.get('warehouse_location') or None
            with transaction.atomic():
                Batch.objects.create(
                    producer=producer,
                    plot=plot,
                    batch_id=request.POST.get('batch_id'),
                    quantity=quantity,
                    warehouse_location_id=warehouse_id,
                    eudr_compliance_status=request.POST.get('eudr_compliance_status'),
                )
                _recalculate_warehouse_stock(warehouse_id)
            messages.success(request, 'Lote registrado correctamente.')
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

def edit_batch(request, pk):
    batch = get_object_or_404(Batch, pk=pk)
    producers = Producer.objects.all()
    warehouses = Warehouse.objects.all()

    if request.method == 'POST':
        producer = get_object_or_404(Producer, pk=request.POST.get('producer'))
        plot = get_object_or_404(Plot, pk=request.POST.get('plot'), producer=producer)
        warehouse_id = request.POST.get('warehouse_location') or None

        try:
            quantity = Decimal(request.POST.get('quantity'))
        except (TypeError, InvalidOperation):
            messages.error(request, 'Ingresa una cantidad válida utilizando solo números.')
        else:
            with transaction.atomic():
                previous_warehouse_id = batch.warehouse_location_id
                batch.producer = producer
                batch.plot = plot
                batch.batch_id = request.POST.get('batch_id')
                batch.quantity = quantity
                batch.warehouse_location_id = warehouse_id
                batch.eudr_compliance_status = request.POST.get('eudr_compliance_status')
                batch.save()

                _recalculate_warehouse_stock(previous_warehouse_id)
                _recalculate_warehouse_stock(warehouse_id)

            messages.success(request, 'Lote actualizado correctamente.')
            return redirect('batch_list')

    plots = Plot.objects.filter(producer=batch.producer)
    return render(
        request,
        'inventory/edit_batch.html',
        {
            'batch': batch,
            'producers': producers,
            'warehouses': warehouses,
            'plots': plots,
        },
    )


def delete_batch(request, pk):
    batch = get_object_or_404(Batch, pk=pk)

    if request.method == 'POST':
        warehouse_id = batch.warehouse_location_id
        batch.delete()
        _recalculate_warehouse_stock(warehouse_id)
        messages.success(request, 'Lote eliminado correctamente.')
        return redirect('batch_list')

    return render(
        request,
        'inventory/delete_batch.html',
        {
            'batch': batch,
        },
    )

def get_producer_plots(request):
    producer_id = request.GET.get('producer_id')
    plots = Plot.objects.filter(producer_id=producer_id).values('id', 'name')
    return JsonResponse(list(plots), safe=False)
