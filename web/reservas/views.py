from django.shortcuts import render
from .models import Reserva

def lista_reservas(request):
    reservas = Reserva.objects.all()
    return render(request, "reservas/lista.html", {"reservas": reservas})
