from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import PuntosFidelizacion

@login_required
def lista_puntos(request):
    puntos = PuntosFidelizacion.objects.all()
    if not request.user.is_staff:
        puntos = puntos.filter(usuario=request.user)
    return render(request, "fidelizacion/lista.html", {"puntos": puntos})
