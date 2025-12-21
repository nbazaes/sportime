from django.urls import path

from . import views

app_name = "fidelizacion"

urlpatterns = [
    path("", views.lista_puntos, name="lista"),
    path("canjear/", views.canjear, name="canjear"),
    path("cancelar/", views.cancelar, name="cancelar"),
]
