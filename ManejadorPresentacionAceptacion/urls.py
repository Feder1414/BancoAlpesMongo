from django.urls import path, include
from .api import CrearSolicitudViewSet
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('api/crearSolicitud/', CrearSolicitudViewSet.as_view(), name='solicitudDocumento/'),
]