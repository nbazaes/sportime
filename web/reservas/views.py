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
    template_name = "reservas/confirm_delete.html"
    success_url = reverse_lazy("reservas:lista")

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

        from fidelizacion.models import PuntosFidelizacion
        from pagos.models import Pago

        self.object = self.get_object()

        user = request.user
        with transaction.atomic():
            pago, created = Pago.objects.get_or_create(
                reserva=self.object,
                defaults={
                    "usuario": user,
                    "monto": 5000,
                    "metodo": "WebPay Sandbox",
                    "estado": "aprobado",
                },
            )

            # Sumar puntos solo la primera vez que se confirma el pago
            if created:
                puntos, _ = PuntosFidelizacion.objects.get_or_create(usuario=user)
                puntos.puntos_acumulados += 15
                puntos.save()

        return HttpResponseRedirect(reverse("pagos:lista"))
