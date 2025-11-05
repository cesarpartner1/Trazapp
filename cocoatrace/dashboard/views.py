from decimal import Decimal

from django.db.models import Sum
from django.shortcuts import render

from core.models import ActivityLog
from infrastructure.models import Warehouse
from inventory.models import Batch
from producers.models import Plot, Producer


def _percentage(amount, total):
    if not total:
        return 0
    return round((amount / total) * 100)


def dashboard(request):
    producer_count = Producer.objects.count()
    plot_count = Plot.objects.count()
    warehouse_count = Warehouse.objects.count()
    batch_count = Batch.objects.count()

    approved_producers = Producer.objects.filter(compliance_status='Approved').count()
    pending_producers = Producer.objects.filter(compliance_status='Pending Review').count()
    rejected_producers = Producer.objects.filter(compliance_status='Rejected').count()

    compliant_plots = Plot.objects.filter(eudr_compliant=True).count()
    active_plots = Plot.objects.filter(is_active=True).count()

    total_batch_weight = Batch.objects.aggregate(total=Sum('quantity'))['total'] or Decimal('0')
    compliant_batches = Batch.objects.filter(eudr_compliance_status='compliant').count()
    pending_batches = Batch.objects.filter(eudr_compliance_status='pending').count()
    non_compliant_batches = Batch.objects.filter(eudr_compliance_status='non_compliant').count()

    total_capacity = Warehouse.objects.aggregate(total=Sum('capacity_kg'))['total'] or Decimal('0')
    current_stock = Warehouse.objects.aggregate(total=Sum('current_stock_kg'))['total'] or Decimal('0')
    warehouse_utilisation = _percentage(float(current_stock), float(total_capacity)) if total_capacity else 0

    compliance_distribution = [
        {
            'label': 'Aprobados',
            'count': approved_producers,
            'percent': _percentage(approved_producers, producer_count),
            'status_class': 'status-approved',
        },
        {
            'label': 'Pendientes por revisar',
            'count': pending_producers,
            'percent': _percentage(pending_producers, producer_count),
            'status_class': 'status-pending-review',
        },
        {
            'label': 'Rechazados',
            'count': rejected_producers,
            'percent': _percentage(rejected_producers, producer_count),
            'status_class': 'status-rejected',
        },
    ]

    batch_status_summary = [
        {
            'label': 'Conformes',
            'count': compliant_batches,
            'percent': _percentage(compliant_batches, batch_count),
            'color': '#16a34a',
        },
        {
            'label': 'Pendientes',
            'count': pending_batches,
            'percent': _percentage(pending_batches, batch_count),
            'color': '#eab308',
        },
        {
            'label': 'No conformes',
            'count': non_compliant_batches,
            'percent': _percentage(non_compliant_batches, batch_count),
            'color': '#dc2626',
        },
    ]

    top_warehouses = Warehouse.objects.order_by('-current_stock_kg')[:5]

    recent_activity = [
        {
            'timestamp': log.created_at,
            'title': log.title,
            'meta': log.meta,
            'category': log.category,
            'event_type': log.event_type,
        }
        for log in ActivityLog.objects.all()[:8]
    ]

    context = {
        'metrics': [
            {
                'label': 'Productores',
                'value': producer_count,
                'subtext': f"{approved_producers} aprobados",
            },
            {
                'label': 'Parcelas',
                'value': plot_count,
                'subtext': f"{compliant_plots} conformes",
            },
            {
                'label': 'Almacenes',
                'value': warehouse_count,
                'subtext': f"{warehouse_utilisation}% de uso",
            },
            {
                'label': 'Lotes',
                'value': batch_count,
                'subtext': f"{total_batch_weight} kg totales",
            },
        ],
        'compliance_distribution': compliance_distribution,
        'batch_status_summary': batch_status_summary,
        'top_warehouses': top_warehouses,
        'recent_activity': recent_activity,
        'active_plots': active_plots,
        'compliant_plots': compliant_plots,
        'warehouse_utilisation': warehouse_utilisation,
        'current_stock': current_stock,
        'total_capacity': total_capacity,
    }

    return render(request, 'dashboard/dashboard.html', context)
