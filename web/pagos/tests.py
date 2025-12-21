from datetime import date, time

from django.contrib.auth import get_user_model
from django.test import TestCase

from reservas.models import Cancha, Reserva

from .models import Pago


class PagoPersistenceTests(TestCase):
	def test_pago_persiste_si_se_elimina_reserva(self):
		User = get_user_model()
		user = User.objects.create_user(username="u1", password="pass")
		cancha = Cancha.objects.create(nombre="Cancha 1", ubicacion="X")
		reserva = Reserva.objects.create(
			usuario=user,
			cancha=cancha,
			fecha=date(2025, 12, 20),
			hora=time(10, 0),
		)
		pago = Pago.objects.create(
			reserva=reserva,
			usuario=user,
			monto=5000,
			metodo="WebPay Sandbox",
			estado="aprobado",
		)

		reserva.delete()

		pago.refresh_from_db()
		self.assertIsNone(pago.reserva)
