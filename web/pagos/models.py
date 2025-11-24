from django.db import models
from django.contrib.auth import get_user_model
from reservas.models import Reserva
User = get_user_model()

class Pago(models.Model):
    reserva = models.OneToOneField(Reserva, on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_pago = models.DateTimeField(auto_now_add=True)
    metodo = models.CharField(max_length=30, default="WebPay Sandbox")
    estado = models.CharField(max_length=20, default="aprobado")

    def __str__(self):
        return f"Pago #{self.id} - {self.usuario} - {self.monto} ({self.estado})"
