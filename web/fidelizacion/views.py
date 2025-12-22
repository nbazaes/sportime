from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import PuntosFidelizacion
from .models import DescuentoRedimido
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages

@login_required
def lista_puntos(request):
    qs = PuntosFidelizacion.objects.all()
    if not request.user.is_staff:
        qs = qs.filter(usuario=request.user)
    return render(request, 'fidelizacion/lista.html', {'qs': qs})


@login_required
def canjear(request):
    # Simple example: define static options
    opciones = [
        {'puntos': 100, 'porcentaje': 5},
        {'puntos': 200, 'porcentaje': 10},
        {'puntos': 500, 'porcentaje': 25},
    ]

    puntos_obj, _ = PuntosFidelizacion.objects.get_or_create(usuario=request.user)

    if request.method == 'POST':
        try:
            idx = int(request.POST.get('opcion'))
            opcion = opciones[idx]
        except Exception:
            messages.error(request, 'Opción inválida')
            return redirect('fidelizacion:lista')

        if puntos_obj.puntos_acumulados < opcion['puntos']:
            messages.error(request, 'No tienes suficientes puntos')
            return redirect('fidelizacion:lista')

        # Create a pending redemption but do NOT deduct points yet.
        # Points will be deducted only when the reservation is confirmed.
        red = DescuentoRedimido.objects.create(
            usuario=request.user,
            porcentaje=opcion['porcentaje'],
            puntos_usados=opcion['puntos'],
        )

        # Store redemption id in session and redirect to reserva create
        request.session['descuento_redimido_id'] = red.id
        return redirect(reverse('reservas:crear'))

    return render(request, 'fidelizacion/canjear.html', {'opciones': opciones, 'puntos': puntos_obj.puntos_acumulados})


@login_required
def cancelar(request):
    # Clear any pending redemption in session when user cancels
    descuento_id = request.session.pop('descuento_redimido_id', None)
    if descuento_id:
        # remove the pending redemption record as it wasn't used
        try:
            DescuentoRedimido.objects.filter(id=descuento_id, usuario=request.user, reserva_num__isnull=True).delete()
        except Exception:
            pass
    messages.info(request, 'Canje cancelado')
    return redirect('fidelizacion:lista')
