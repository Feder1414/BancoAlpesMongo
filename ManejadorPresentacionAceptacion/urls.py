from django.urls import path, include
from .api import CrearSolicitudViewSet, CrearOfertaViewSet, GetOfertasCliente
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('api/crearSolicitud/', CrearSolicitudViewSet.as_view(), name='solicitudDocumento/'),
    path('api/crearOferta/', CrearOfertaViewSet.as_view(), name='ofertaDocumento/'),
    path('api/getOfertas/', GetOfertasCliente.as_view(), name='ofertaDocumento/'),
]