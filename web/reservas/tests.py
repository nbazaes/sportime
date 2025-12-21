from datetime import date, time, timedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.test.utils import override_settings
from django.utils import timezone

from .forms import ReservaForm
from .models import Cancha, Reserva
from django.urls import reverse
from fidelizacion.models import DescuentoRedimido


@override_settings(ALLOWED_HOSTS=["testserver", "localhost", "127.0.0.1"])
class ReservaCancelacionReversaTests(TestCase):
	def test_cancelar_reserva_crea_reversa_en_pagos(self):
		from django.test import Client

		from pagos.models import Pago

		User = get_user_model()
		user = User.objects.create_user(username="u_cancel", password="pass")
		cancha = Cancha.objects.create(nombre="Cancha 1", ubicacion="X")
		reserva = Reserva.objects.create(
			usuario=user,
			cancha=cancha,
			fecha=timezone.localdate() + timedelta(days=1),
			hora=(timezone.localtime(timezone.now()) + timedelta(hours=1)).time().replace(microsecond=0),
			estado="confirmada",
		)
		Pago.objects.create(
			reserva=reserva,
			usuario=user,
			monto=5000,
			metodo="WebPay Sandbox",
			estado="aprobado",
		)

		client = Client()
		self.assertTrue(client.login(username="u_cancel", password="pass"))
		resp = client.post(f"/reservas/{reserva.id}/eliminar/")
		self.assertEqual(resp.status_code, 302)
		self.assertFalse(Reserva.objects.filter(id=reserva.id).exists())

		reversas = Pago.objects.filter(usuario=user, metodo="Reversa", estado="reversado")
		self.assertEqual(reversas.count(), 1)
		self.assertEqual(reversas.first().monto, -5000)



class ReservaFormTimeValidationTests(TestCase):
	def setUp(self):
		User = get_user_model()
		self.user = User.objects.create_user(username="u1", password="pass")
		self.cancha = Cancha.objects.create(nombre="Cancha 1", ubicacion="X")

	def test_no_permite_reserva_en_pasado(self):
		past = timezone.localtime(timezone.now()) - timedelta(hours=1)

		form = ReservaForm(
			data={
				"cancha": self.cancha.id,
				"fecha": past.date(),
				"hora": past.time().replace(microsecond=0),
				"estado": "confirmada",
			},
			user=self.user,
		)
		self.assertFalse(form.is_valid())
		self.assertIn("No puedes reservar una hora previa a la actual.", form.non_field_errors())

	def test_model_clean_bloquea_fecha_muy_pasada(self):
		reserva = Reserva(
			usuario=self.user,
			cancha=self.cancha,
			fecha=date(1111, 1, 1),
			hora=time(10, 0),
			estado="confirmada",
		)

		with self.assertRaisesMessage(ValidationError, "No puedes reservar una hora previa a la actual."):
			reserva.full_clean()

	def test_form_muestra_banner_descuento_si_hay_redencion_pendiente(self):
		# preparar usuario y sesión con redención
		User = get_user_model()
		user = User.objects.create_user(username='u_banner', password='pass')
		cancha = Cancha.objects.create(nombre='C2', ubicacion='Y')
		red = DescuentoRedimido.objects.create(usuario=user, porcentaje=10, puntos_usados=200)

		client = self.client
		client.force_login(user)
		# set session key
		s = client.session
		s['descuento_redimido_id'] = red.id
		s.save()

		resp = client.get(reverse('reservas:crear'))
		self.assertEqual(resp.status_code, 200)
		# Banner should display porcentaje and discounted price (e.g., 10% and $4500)
		self.assertContains(resp, f"{red.porcentaje}%")
		self.assertContains(resp, "$4500")

