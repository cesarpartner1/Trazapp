from decimal import Decimal

from django.db.models import Sum
from django.shortcuts import render

from infrastructure.models import Warehouse
from inventory.models import Batch
from producers.models import Document, Plot, Producer


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
            'label': 'Approved',
            'count': approved_producers,
            'percent': _percentage(approved_producers, producer_count),
            'status_class': 'status-approved',
        },
        {
            'label': 'Pending Review',
            'count': pending_producers,
            'percent': _percentage(pending_producers, producer_count),
            'status_class': 'status-pending-review',
        },
        {
            'label': 'Rejected',
            'count': rejected_producers,
            'percent': _percentage(rejected_producers, producer_count),
            'status_class': 'status-rejected',
        },
    ]

    batch_status_summary = [
        {
            'label': 'Compliant',
            'count': compliant_batches,
            'percent': _percentage(compliant_batches, batch_count),
            'color': '#16a34a',
        },
        {
            'label': 'Pending',
            'count': pending_batches,
            'percent': _percentage(pending_batches, batch_count),
            'color': '#eab308',
        },
        {
            'label': 'Non-Compliant',
            'count': non_compliant_batches,
            'percent': _percentage(non_compliant_batches, batch_count),
            'color': '#dc2626',
        },
    ]

    top_warehouses = Warehouse.objects.order_by('-current_stock_kg')[:5]

    activity_events = []

    for producer in Producer.objects.order_by('-created_at')[:5]:
        activity_events.append(
            {
                'timestamp': producer.created_at,
                'title': f"New producer onboarded: {producer.full_name}",
                'meta': producer.code,
                'category': 'Producer',
            }
        )

    for plot in Plot.objects.order_by('-created_at')[:5]:
        activity_events.append(
            {
                'timestamp': plot.created_at,
                'title': f"Plot added: {plot.name}",
                'meta': plot.plot_code,
                'category': 'Plot',
            }
        )

    for document in Document.objects.select_related('producer').order_by('-uploaded_at')[:5]:
        activity_events.append(
            {
                'timestamp': document.uploaded_at,
                'title': f"Document uploaded for {document.producer.full_name}",
                'meta': document.name,
                'category': 'Document',
            }
        )

    for batch in Batch.objects.select_related('producer').order_by('-created_at')[:5]:
        activity_events.append(
            {
                'timestamp': batch.created_at,
                'title': f"Batch registered: {batch.batch_id}",
                'meta': batch.producer.full_name,
                'category': 'Inventory',
            }
        )

    recent_activity = sorted(activity_events, key=lambda event: event['timestamp'], reverse=True)[:8]

    context = {
        'metrics': [
            {
                'label': 'Producers',
                'value': producer_count,
                'subtext': f"{approved_producers} approved",
            },
            {
                'label': 'Plots',
                'value': plot_count,
                'subtext': f"{compliant_plots} compliant",
            },
            {
                'label': 'Warehouses',
                'value': warehouse_count,
                'subtext': f"{warehouse_utilisation}% utilisation",
            },
            {
                'label': 'Batches',
                'value': batch_count,
                'subtext': f"{total_batch_weight} kg total",
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
