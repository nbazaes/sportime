from django.contrib import admin
from .models import Pago

@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ("id", "usuario", "monto", "metodo", "estado", "fecha_pago")
    list_filter = ("estado", "metodo")
