from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .forms import ReservaForm
from .models import Reserva


class ReservaListView(LoginRequiredMixin, ListView):
    model = Reserva
    template_name = "reservas/lista.html"
    context_object_name = "reservas"
    ordering = ["-fecha", "-hora"]

    def get_queryset(self):
        qs = super().get_queryset()
        user = getattr(self.request, "user", None)
        if user is not None and getattr(user, "is_authenticated", False) and not getattr(
            user, "is_staff", False
        ):
            return qs.filter(usuario=user)
        return qs


class ReservaDetailView(LoginRequiredMixin, DetailView):
    model = Reserva
    template_name = "reservas/detalle.html"
    context_object_name = "reserva"

    def get_queryset(self):
        qs = super().get_queryset()
        user = getattr(self.request, "user", None)
        if user is not None and getattr(user, "is_authenticated", False) and not getattr(
            user, "is_staff", False
        ):
            return qs.filter(usuario=user)
        return qs


class ReservaCreateView(LoginRequiredMixin, CreateView):
    model = Reserva
    form_class = ReservaForm
    template_name = "reservas/form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = getattr(self.request, "user", None)
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        request = self.request
        descuento_id = request.session.get('descuento_redimido_id')
        contexto_desc = None
        if descuento_id:
            from fidelizacion.models import DescuentoRedimido
            red = DescuentoRedimido.objects.filter(id=descuento_id, usuario=request.user, reserva_num__isnull=True).first()
            if red:
                monto_base = 5000
                monto_desc = int(monto_base * (100 - red.porcentaje) / 100)
                contexto_desc = {
                    'porcentaje': red.porcentaje,
                    'monto_base': monto_base,
                    'monto_desc': monto_desc,
                }

        context['descuento_pending'] = contexto_desc
        return context

    def form_valid(self, form):
        user = getattr(self.request, "user", None)
        if user is not None and getattr(user, "is_authenticated", False) and not getattr(
            user, "is_staff", False
        ):
            form.instance.usuario = user
        response = super().form_valid(form)
        return response

    def get_success_url(self):
        return reverse("reservas:confirmar_pago", kwargs={"pk": self.object.pk})


class ReservaUpdateView(LoginRequiredMixin, UpdateView):
    model = Reserva
    form_class = ReservaForm
    template_name = "reservas/form.html"
    success_url = reverse_lazy("reservas:lista")

    def get_queryset(self):
        qs = super().get_queryset()
        user = getattr(self.request, "user", None)
        if user is not None and getattr(user, "is_authenticated", False) and not getattr(
            user, "is_staff", False
        ):
            return qs.filter(usuario=user)
        return qs

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = getattr(self.request, "user", None)
        return kwargs

    def form_valid(self, form):
        user = getattr(self.request, "user", None)
        if user is not None and getattr(user, "is_authenticated", False) and not getattr(
            user, "is_staff", False
        ):
            form.instance.usuario = user
        return super().form_valid(form)


class ReservaDeleteView(LoginRequiredMixin, DeleteView):
    model = Reserva
    success_url = reverse_lazy("reservas:lista")
    http_method_names = ["post"]

    def get_queryset(self):
        qs = super().get_queryset()
        user = getattr(self.request, "user", None)
        if user is not None and getattr(user, "is_authenticated", False) and not getattr(
            user, "is_staff", False
        ):
            return qs.filter(usuario=user)
        return qs


class ReservaConfirmarPagoView(LoginRequiredMixin, DetailView):
    model = Reserva
    template_name = "reservas/confirmar_pago.html"
    context_object_name = "reserva"

    def get_queryset(self):
        qs = super().get_queryset()
        user = getattr(self.request, "user", None)
        if user is not None and getattr(user, "is_authenticated", False) and not getattr(
            user, "is_staff", False
        ):
            return qs.filter(usuario=user)
        return qs

    def post(self, request, *args, **kwargs):
        from django.db import transaction

        from fidelizacion.models import PuntosFidelizacion, DescuentoRedimido
        from pagos.models import Pago

        self.object = self.get_object()

        user = request.user
        # Check for a pending redemption in session
        descuento_id = request.session.pop('descuento_redimido_id', None)

        with transaction.atomic():
            porcentaje = None
            if descuento_id:
                red = DescuentoRedimido.objects.filter(id=descuento_id, usuario=user, reserva_num__isnull=True).first()
                if red:
                    porcentaje = red.porcentaje

            monto_base = 5000
            if porcentaje:
                monto = int(monto_base * (100 - porcentaje) / 100)
            else:
                monto = monto_base

            pago, created = Pago.objects.get_or_create(
                reserva=self.object,
                defaults={
                    "usuario": user,
                    "monto": monto,
                    "metodo": "WebPay Sandbox",
                    "estado": "aprobado",
                    "reserva_num": self.object.id,
                },
            )

            # If redemption was applied, mark it with reserva_num
            if descuento_id and red and created:
                red.reserva_num = self.object.id
                red.save()

            # If redemption was applied, deduct the user's points now (only once)
            if descuento_id and red and created:
                try:
                    puntos_obj, _ = PuntosFidelizacion.objects.get_or_create(usuario=user)
                    # only deduct if they still have enough points (safety)
                    if puntos_obj.puntos_acumulados >= red.puntos_usados:
                        puntos_obj.puntos_acumulados -= red.puntos_usados
                        puntos_obj.save()
                except Exception:
                    # don't block payment flow on points errors
                    pass

            # Sumar puntos solo la primera vez que se confirma el pago
            if created:
                puntos, _ = PuntosFidelizacion.objects.get_or_create(usuario=user)
                puntos.puntos_acumulados += 15
                puntos.save()

        return HttpResponseRedirect(reverse("pagos:lista"))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        request = self.request
        from fidelizacion.models import DescuentoRedimido
        descuento_id = request.session.get('descuento_redimido_id')
        contexto_desc = None
        if descuento_id:
            try:
                red = DescuentoRedimido.objects.filter(id=descuento_id, usuario=request.user, reserva_num__isnull=True).first()
                if red:
                    monto_base = 5000
                    monto_desc = int(monto_base * (100 - red.porcentaje) / 100)
                    contexto_desc = {
                        'porcentaje': red.porcentaje,
                        'monto_base': monto_base,
                        'monto_desc': monto_desc,
                    }
            except Exception:
                contexto_desc = None

        context['descuento_pending'] = contexto_desc
        return context
