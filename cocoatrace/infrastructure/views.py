from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from core.models import ActivityLog
from core.utils import log_activity
from .forms import WarehouseForm
from .models import Warehouse


def warehouse_list(request):
	warehouses = Warehouse.objects.all().order_by('name')
	return render(
		request,
		'infrastructure/warehouse_list.html',
		{
			'warehouses': warehouses,
		},
	)


def warehouse_create(request):
	form = WarehouseForm(request.POST or None)

	if request.method == 'POST':
		if form.is_valid():
			warehouse = form.save()
			log_activity('Almacén', f"Almacén registrado: {warehouse.name}", warehouse.code, event_type=ActivityLog.EVENT_CREATE)
			messages.success(request, 'Almacén registrado correctamente.')
			return redirect('warehouse_list')
		messages.error(request, 'Soluciona los errores e intenta de nuevo.')

	return render(
		request,
		'infrastructure/warehouse_form.html',
		{
			'form': form,
			'page_subtitle': 'Red logística',
			'page_title': 'Nuevo almacén',
			'page_helper': 'Registra un centro de acopio para habilitar el enrutamiento de lotes y los reportes de cumplimiento.',
			'cancel_url': 'warehouse_list',
			'submit_label': 'Guardar almacén',
		},
	)


def warehouse_update(request, pk):
	warehouse = get_object_or_404(Warehouse, pk=pk)
	form = WarehouseForm(request.POST or None, instance=warehouse)

	if request.method == 'POST':
		if form.is_valid():
			warehouse = form.save()
			log_activity('Almacén', f"Almacén actualizado: {warehouse.name}", warehouse.code, event_type=ActivityLog.EVENT_UPDATE)
			messages.success(request, 'Almacén actualizado correctamente.')
			return redirect('warehouse_list')
		messages.error(request, 'Revisa la información e intenta nuevamente.')

	return render(
		request,
		'infrastructure/warehouse_form.html',
		{
			'form': form,
			'page_subtitle': warehouse.code,
			'page_title': 'Editar almacén',
			'page_helper': 'Actualiza la información del centro de acopio seleccionado.',
			'cancel_url': 'warehouse_list',
			'submit_label': 'Actualizar almacén',
			'is_edit': True,
			'warehouse': warehouse,
		},
	)


def warehouse_delete(request, pk):
	warehouse = get_object_or_404(Warehouse, pk=pk)

	if request.method == 'POST':
		name = warehouse.name
		code = warehouse.code
		warehouse.delete()
		log_activity('Almacén', f"Almacén eliminado: {name}", code, event_type=ActivityLog.EVENT_DELETE)
		messages.success(request, 'Almacén eliminado correctamente.')
		return redirect('warehouse_list')

	return render(
		request,
		'infrastructure/warehouse_confirm_delete.html',
		{
			'warehouse': warehouse,
		},
	)
