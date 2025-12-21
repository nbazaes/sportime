from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("pagos", "0002_alter_pago_reserva_set_null"),
    ]

    operations = [
        migrations.AddField(
            model_name="pago",
            name="reserva_num",
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
