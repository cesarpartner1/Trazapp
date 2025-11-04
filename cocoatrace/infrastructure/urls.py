from django.urls import path

from . import views

urlpatterns = [
    path('warehouses/', views.warehouse_list, name='warehouse_list'),
    path('warehouses/new/', views.warehouse_create, name='warehouse_create'),
]
