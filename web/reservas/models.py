import datetime

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

User = get_user_model()

class Cancha(models.Model):
    nombre = models.CharField(max_length=100)
    ubicacion = models.CharField(max_length=150)

    def __str__(self):
        return self.nombre

class Reserva(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    cancha = models.ForeignKey(Cancha, on_delete=models.CASCADE)
    fecha = models.DateField()
    hora = models.TimeField()
    estado = models.CharField(max_length=20, default='confirmada')

    def clean(self):
        super().clean()
        if self.fecha is None or self.hora is None:
            return

        now_local = timezone.localtime(timezone.now())
        reserva_dt = timezone.make_aware(
            datetime.datetime.combine(self.fecha, self.hora),
            timezone.get_current_timezone(),
        )

        if reserva_dt < now_local:
            raise ValidationError("No puedes reservar una hora previa a la actual.")

    def __str__(self):
        return f"{self.usuario} - {self.cancha} ({self.fecha} {self.hora})"
