from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Solicitud, SolicitudesRecientes, Oferta , SolicitudEmbebida, Contador
import requests
from bson.json_util import dumps, default
from django.conf import settings
from .logic import validate_jwt
import time


def checkCliente(idCliente, token):
    headers = {'Authorization': 'Bearer ' + token}
    cliente = requests.get(settings.PATH_PER + str(idCliente) + "/", headers=headers)
    if cliente.status_code != 200:
        return False, cliente
    return True, cliente

class CrearSolicitudViewSet(APIView):
    def post(self, request):
        token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
        payload = validate_jwt(token)
        idCliente = request.data.get('idCliente')
        if idCliente == None:
            return Response(data = "No se envio el id del cliente",status=status.HTTP_400_BAD_REQUEST)
        if token == None:
            return Response(data = "No se envio el token",status=status.HTTP_400_BAD_REQUEST)
        clienteExiste, cliente = checkCliente(idCliente, token)
        cliente = cliente.json()
        if not clienteExiste:
            return Response(data = "No se encontro el cliente",status=status.HTTP_404_NOT_FOUND)
        if payload["idPersona"] != cliente["id"]:
            return Response(data = "No tiene autorizacion para acceder a este recurso",status=status.HTTP_403_FORBIDDEN)
   
        ContadorSolicitud = Contador.objects().first()
        idSolicitud = 0
        if ContadorSolicitud == None:
            idSolicitud = 0
            ContadorSolicitud = Contador(idSolicitud=idSolicitud+1, idOferta=0)
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
        token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
        payload = validate_jwt(token)
        idSolicitud = request.data.get('idSolicitud')
        solicitud = Solicitud.objects(idSolicitud=idSolicitud).first()
        if solicitud == None:
            return Response(data = "No se encontro la solicitud",status=status.HTTP_404_NOT_FOUND)
        idCliente = solicitud.idCliente
        existe,cliente = checkCliente(idCliente, token)
        cliente = cliente.json()
        if payload["idPersona"] != cliente["id"]:
            return Response(data = "No tiene autorizacion para acceder a este recurso",status=status.HTTP_403_FORBIDDEN)
        if not existe:
            return Response(data = "No se encontro el cliente",status=status.HTTP_404_NOT_FOUND)
        if cliente["informacion_financiera"] == None:
            return Response(data = "El cliente no tiene informacion financiera",status=status.HTTP_404_NOT_FOUND)
        if cliente["informacion_financiera"]["ingresos"] < cliente["informacion_financiera"]["egresos"]:
            return Response(data = "El cliente no tiene capacidad de pago",status=status.HTTP_404_NOT_FOUND)
        
        #url = "http://localhost:8069/api/ofertas/generar-oferta/"
        url = "http://10.128.0.5:8080/api/ofertas/generar-oferta/"
        oferta = requests.post(url, json= cliente["informacion_financiera"])
        if oferta.status_code != 201:
            return Response(data = "No se pudo generar la oferta",status=status.HTTP_404_NOT_FOUND)
        oferta = oferta.json()
        contador = Contador.objects().first()
        idOferta = contador.idOferta
        contador.idOferta += 1
        contador.save()
        ofertaMongo = Oferta(idOferta = idOferta,**oferta)
        solicitud.ofertas.append(ofertaMongo)
        solicitud_cliente_reciente = SolicitudesRecientes.objects(idCliente=solicitud.idCliente).first()
        solicitudes_recientes = solicitud_cliente_reciente.solicitudes
        for solicitud_reciente in solicitudes_recientes:
            if solicitud_reciente.idSolicitud == solicitud.idSolicitud:
                solicitud_reciente.ofertas.append(ofertaMongo)
        solicitud.save()
        solicitud_cliente_reciente.save()
        return Response(data = oferta,status=status.HTTP_201_CREATED)
    
class GetOfertasCliente(APIView):
    def post(self, request):
        token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
        payload = validate_jwt(token)
        start_time = time.time()
        idCliente = request.data.get('idCliente')
        if idCliente == None:
            return Response(data = "No se envio el id del cliente",status=status.HTTP_400_BAD_REQUEST)
        existe, cliente = checkCliente(idCliente, token)
        cliente = cliente.json()
        if not existe:
            return Response(data = "No se encontro el cliente",status=status.HTTP_404_NOT_FOUND)
        if payload["idPersona"] != cliente["id"]:
            return Response(data = "No tiene autorizacion para acceder a este recurso",status=status.HTTP_403_FORBIDDEN)    
        solicitudes_recientes = SolicitudesRecientes.objects(idCliente=idCliente).first()
        if solicitudes_recientes == None:
            return Response(data = "No se encontraron solicitudes para este cliente",status=status.HTTP_404_NOT_FOUND)
        ofertas = []

        if solicitudes_recientes.cantidadSolicitudes  > 10:
            solicitudes = Solicitud.objects(idCliente=idCliente)
            for solicitud in solicitudes:
                for oferta in solicitud.ofertas:
                    ofertas.append(oferta.to_mongo().to_dict())
        else:
            for solicitud in solicitudes_recientes.solicitudes:
                for oferta in solicitud.ofertas:
                    ofertas.append(oferta.to_mongo().to_dict())

        ofertas_json = dumps(ofertas, default=default)

        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"La función se ejecutó en {elapsed_time} segundos")

        return Response(data = ofertas_json,status=status.HTTP_200_OK)
            


        

        




        