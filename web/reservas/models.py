from django.db import models
from django.contrib.auth import get_user_model
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

    def __str__(self):
        return f"{self.usuario} - {self.cancha} ({self.fecha} {self.hora})"
