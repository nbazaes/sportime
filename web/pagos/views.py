from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Pago

@login_required
def lista_pagos(request):
    pagos = Pago.objects.all().order_by("-fecha_pago", "-id")
    if not request.user.is_staff:
        pagos = pagos.filter(usuario=request.user)
    return render(request, "pagos/lista.html", {"pagos": pagos})
