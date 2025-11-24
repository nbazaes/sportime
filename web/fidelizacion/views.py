from django.shortcuts import render
from .models import PuntosFidelizacion

def lista_puntos(request):
    puntos = PuntosFidelizacion.objects.all()
    return render(request, "fidelizacion/lista.html", {"puntos": puntos})
