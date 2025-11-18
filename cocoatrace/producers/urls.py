from django.urls import path
from . import views

urlpatterns = [
    path('producers/', views.producer_list, name='producer_list'),
    path('producers/new/', views.create_producer, name='create_producer'),
    path('producers/<int:pk>/editar/', views.edit_producer, name='edit_producer'),
    path('producers/<int:pk>/eliminar/', views.delete_producer, name='delete_producer'),
    path('producers/<int:pk>/', views.producer_detail, name='producer_detail'),
    path('producers/<int:pk>/dossier/', views.producer_dossier, name='producer_dossier'),
    path('producers/<int:producer_pk>/add_plot/', views.add_plot, name='add_plot'),
    path('producers/<int:producer_pk>/plots/<int:plot_pk>/editar/', views.edit_plot, name='edit_plot'),
    path('producers/<int:producer_pk>/plots/<int:plot_pk>/', views.plot_detail, name='plot_detail'),
    path('producers/<int:producer_pk>/documents/<int:document_pk>/edit/', views.edit_document, name='edit_document'),
    path('producers/<int:producer_pk>/documents/<int:document_pk>/delete/', views.delete_document, name='delete_document'),
]
