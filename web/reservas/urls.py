from django.urls import path

from . import views

app_name = "reservas"

urlpatterns = [
    path("", views.ReservaListView.as_view(), name="lista"),
    path("nueva/", views.ReservaCreateView.as_view(), name="crear"),
    path("<int:pk>/confirmar-pago/", views.ReservaConfirmarPagoView.as_view(), name="confirmar_pago"),
    path("<int:pk>/", views.ReservaDetailView.as_view(), name="detalle"),
    path("<int:pk>/editar/", views.ReservaUpdateView.as_view(), name="editar"),
    path("<int:pk>/eliminar/", views.ReservaDeleteView.as_view(), name="eliminar"),
]
