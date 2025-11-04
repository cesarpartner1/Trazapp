from django.contrib import messages
from django.shortcuts import redirect, render

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
			messages.success(request, 'Warehouse registered successfully.')
			return redirect('warehouse_list')
		messages.error(request, 'Resolve the errors below and try again.')

	return render(
		request,
		'infrastructure/warehouse_form.html',
		{
			'form': form,
		},
	)
