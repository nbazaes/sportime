from django.db.models.signals import pre_delete
from django.dispatch import receiver

from pagos.models import Pago

from .models import Reserva


@receiver(pre_delete, sender=Reserva)
def crear_reversa_pago_al_cancelar_reserva(sender, instance: Reserva, **kwargs):
    pago = (
        Pago.objects.filter(reserva=instance)
        .order_by("-fecha_pago", "-id")
        .first()
    )
    if pago is None or pago.monto is None or pago.monto <= 0:
        return

    Pago.objects.create(
        reserva=None,
        usuario=pago.usuario,
        monto=-pago.monto,
        metodo="Reversa",
        estado="reversado",
        reserva_num=instance.id,
    )
