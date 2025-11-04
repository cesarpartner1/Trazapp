from django.urls import path
from . import views

urlpatterns = [
    path('inventory/', views.batch_list, name='batch_list'),
    path('inventory/create/', views.create_batch, name='create_batch'),
    path('ajax/get_producer_plots/', views.get_producer_plots, name='get_producer_plots'),
]
