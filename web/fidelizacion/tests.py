from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
import datetime

from .models import PuntosFidelizacion, DescuentoRedimido
from reservas.models import Cancha, Reserva
from pagos.models import Pago


class RedeemReserveConfirmFlowTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='tester', password='pass')
        self.cancha = Cancha.objects.create(nombre='C1', ubicacion='X')
        self.puntos = PuntosFidelizacion.objects.create(usuario=self.user, puntos_acumulados=200)

    def test_redeem_and_reserve_and_confirm_applies_discount(self):
        self.client.force_login(self.user)

        # Redeem option index 1 => 200 pts -> 10%
        resp = self.client.post(reverse('fidelizacion:canjear'), data={'opcion': '1'}, follow=True)
        self.assertEqual(resp.status_code, 200)

        red = DescuentoRedimido.objects.filter(usuario=self.user).first()
        self.assertIsNotNone(red)
        self.assertEqual(red.porcentaje, 10)

        session = self.client.session
        self.assertEqual(session.get('descuento_redimido_id'), red.id)

        # Create reservation for tomorrow at 12:00
        fecha_date = timezone.localdate() + datetime.timedelta(days=1)
        hora_time = datetime.time(hour=12, minute=0)

        create_resp = self.client.post(
            reverse('reservas:crear'),
            data={
                'cancha': self.cancha.id,
                'fecha': fecha_date.isoformat(),
                'hora': hora_time.strftime('%H:%M'),
                'estado': 'confirmada',
            },
            follow=True,
        )
        self.assertEqual(create_resp.status_code, 200)

        reserva = Reserva.objects.get(usuario=self.user, cancha=self.cancha, fecha=fecha_date, hora=hora_time)

        # Confirm payment
        confirm_url = reverse('reservas:confirmar_pago', kwargs={'pk': reserva.pk})
        post_resp = self.client.post(confirm_url, follow=True)
        self.assertEqual(post_resp.status_code, 200)

        pago = Pago.objects.filter(reserva=reserva).first()
        self.assertIsNotNone(pago)

        expected = (5000 * (100 - red.porcentaje)) // 100
        self.assertEqual(int(pago.monto), expected)

        red.refresh_from_db()
        self.assertEqual(red.reserva_num, reserva.id)
from django.test import TestCase

# Create your tests here.
