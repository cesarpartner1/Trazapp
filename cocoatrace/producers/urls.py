from django.urls import path
from . import views

urlpatterns = [
    path('producers/', views.producer_list, name='producer_list'),
    path('producers/<int:pk>/', views.producer_detail, name='producer_detail'),
    path('producers/<int:producer_pk>/add_plot/', views.add_plot, name='add_plot'),
]
