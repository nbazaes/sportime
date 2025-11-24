from django.contrib import admin
from django.urls import path
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('reservas/', TemplateView.as_view(template_name='reservas.html'), name='reservas'),
    path('pagos/', TemplateView.as_view(template_name='pagos.html'), name='pagos'),
    path('fidelizacion/', TemplateView.as_view(template_name='fidelizacion.html'), name='fidelizacion'),
]
