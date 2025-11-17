from django.urls import path

from . import views

app_name = "eudr"

urlpatterns = [
    path("", views.DiligenceListView.as_view(), name="diligence_list"),
    path("nueva/", views.DiligenceCreateView.as_view(), name="diligence_create"),
    path("<uuid:public_id>/", views.DiligenceDetailView.as_view(), name="diligence_detail"),
    path("<uuid:public_id>/timeline/", views.TimelineEntryCreateView.as_view(), name="timeline_create"),
    path("<uuid:public_id>/producers/", views.AttachProducerView.as_view(), name="attach_producers"),
    path(
        "<uuid:public_id>/producers/<int:pk>/eliminar/",
        views.DetachProducerView.as_view(),
        name="detach_producer",
    ),
]
