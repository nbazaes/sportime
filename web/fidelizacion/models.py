from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()

class PuntosFidelizacion(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    puntos_acumulados = models.PositiveIntegerField(default=0)
    fecha_ultima_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.usuario.username} - {self.puntos_acumulados} pts"


class DescuentoRedimido(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    porcentaje = models.PositiveIntegerField()
    puntos_usados = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    reserva_num = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.usuario.username} - {self.porcentaje}% - {self.puntos_usados} pts"
