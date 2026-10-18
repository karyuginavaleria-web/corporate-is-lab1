from django.urls import path

from . import views


urlpatterns = [
    path("", views.ticket_list, name="ticket_list"),
    path("new/", views.ticket_create, name="ticket_create"),
    path("queue/", views.ticket_queue, name="ticket_queue"),
    path("<int:pk>/", views.ticket_detail, name="ticket_detail"),
    path("<int:pk>/edit/", views.ticket_update, name="ticket_update"),
]