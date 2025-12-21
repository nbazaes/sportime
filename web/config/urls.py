from django.contrib import admin
from django.urls import include, path
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView
from . import views as config_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),

    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', config_views.register, name='register'),

    path('reservas/', include('reservas.urls')),
    path('pagos/', include('pagos.urls')),
    path('fidelizacion/', include('fidelizacion.urls')),
]
