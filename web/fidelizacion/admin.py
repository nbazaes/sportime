from django.contrib import admin
from .models import PuntosFidelizacion

@admin.register(PuntosFidelizacion)
class PuntosAdmin(admin.ModelAdmin):
    list_display = ("usuario", "puntos_acumulados", "fecha_ultima_actualizacion")
