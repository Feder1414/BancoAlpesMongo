from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Solicitud, SolicitudesRecientes, Oferta , SolicitudEmbebida, Contador
import requests
from bson.json_util import dumps
from django.conf import settings


def checkCliente(idCliente, token):
    headers = {'Authorization': 'Bearer ' + token}
    cliente = requests.get(settings.PATH_PER + str(idCliente) + "/", headers=headers)
    if cliente.status_code != 200:
        return False, cliente
    return True, cliente

class CrearSolicitudViewSet(APIView):
    def post(self, request):
        idCliente = request.data.get('idCliente')
        token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
        if idCliente == None:
            return Response(data = "No se envio el id del cliente",status=status.HTTP_400_BAD_REQUEST)
        if token == None:
            return Response(data = "No se envio el token",status=status.HTTP_400_BAD_REQUEST)
        clienteExiste, cliente = checkCliente(idCliente, token)
        print(clienteExiste, cliente.json())
        if not clienteExiste:
            return Response(data = "No se encontro el cliente",status=status.HTTP_404_NOT_FOUND)
        print(cliente.json())
        ContadorSolicitud = Contador.objects().first()
        idSolicitud = 0
        if ContadorSolicitud == None:
            idSolicitud = 0
            ContadorSolicitud = Contador(idSolicitud=idSolicitud+1)
            ContadorSolicitud.save()
        else:
            idSolicitud = ContadorSolicitud.idSolicitud
            ContadorSolicitud.idSolicitud += 1
            ContadorSolicitud.save()
        solicitud = Solicitud(idSolicitud=idSolicitud, estado='Nueva', idCliente=idCliente, ofertas = [])
        solicitudEmbebida = SolicitudEmbebida(idSolicitud=idSolicitud, estado='Nueva', ofertas = [])
        solicitudes_recientes = SolicitudesRecientes.objects(idCliente=idCliente).first()
        if solicitudes_recientes:
            if len(solicitudes_recientes.solicitudes) == 10:
                solicitudes_recientes.solicitudes.pop(0)
                
            solicitudes_recientes.solicitudes.append(solicitudEmbebida)
            solicitudes_recientes.cantidadSolicitudes += 1
        else:
            solicitudes_recientes = SolicitudesRecientes(idCliente=idCliente, solicitudes=[solicitudEmbebida], cantidadSolicitudes=1)
        
        solicitud.save()
        solicitudes_recientes.save()

        solicitud_dict = solicitud.to_mongo().to_dict()
        solicitud_json = dumps(solicitud_dict)


        return Response(data = solicitud_json,status=status.HTTP_201_CREATED)
    
class CrearOfertaViewSet(APIView):
    def post(self, request):
        idSolicitud = request.data.get('idSolicitud')
        solicitud = SolicitudEmbebida.objects(id=idSolicitud)[0].first()
        if solicitud == None:
            return Response(data = "No se encontro la solicitud",status=status.HTTP_404_NOT_FOUND)
        idCliente = {'idCliente': solicitud.idCliente}
        url = "http://10.128.0.5:8080/api/ofertas/generar-oferta/"
        clienteSolicitud = requests.post(url, json=idCliente)
        clienteSolicitudDict = clienteSolicitud.json()
        if (len(clienteSolicitudDict) == 0):
            return Response(data = "No se encontro el cliente",status=status.HTTP_404_NOT_FOUND)
        if ["informacionFinanciera"] not in clienteSolicitudDict:
            return Response(data = "El cliente no tiene informaciónFinanciera" ,status=status.HTTP_404_NOT_FOUND)
        if clienteSolicitudDict["informacionFinanciera"]["ingresos"] < clienteSolicitudDict["informacionFinanciera"]["egresos"]:
            return Response(data = "El cliente no tiene capacidad de pago",status=status.HTTP_404_NOT_FOUND)
        
        url2 = "http://10.128.0.5:8080/api/ofertas/generar-oferta/"

        oferta = requests.post(url2, json= clienteSolicitudDict)["informacionFinanciera"]

        return Response(data = oferta,status=status.HTTP_201_CREATED)


        

        




        