from django.urls import path

from . import views

app_name = "surveys"

urlpatterns = [
    path("surveys/import/", views.import_geojson, name="import_geojson"),
]
