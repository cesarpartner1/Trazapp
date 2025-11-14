from django.urls import path

from . import views

app_name = "surveys"

urlpatterns = [
    path("surveys/", views.survey_list, name="survey_list"),
    path("surveys/<int:pk>/", views.survey_detail, name="survey_detail"),
    path("surveys/import/", views.import_geojson, name="import_geojson"),
]
