from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

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
			form.save()
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
			form.save()
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
		warehouse.delete()
		messages.success(request, 'Almacén eliminado correctamente.')
		return redirect('warehouse_list')

	return render(
		request,
		'infrastructure/warehouse_confirm_delete.html',
		{
			'warehouse': warehouse,
		},
	)
