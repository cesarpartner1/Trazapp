from django.urls import path

from . import views

urlpatterns = [
    path('warehouses/', views.warehouse_list, name='warehouse_list'),
    path('warehouses/new/', views.warehouse_create, name='warehouse_create'),
    path('warehouses/<int:pk>/editar/', views.warehouse_update, name='warehouse_update'),
    path('warehouses/<int:pk>/eliminar/', views.warehouse_delete, name='warehouse_delete'),
]
