from mongoengine import Document, StringField, IntField, ListField, EmbeddedDocument, EmbeddedDocumentField, DecimalField

class  Oferta(EmbeddedDocument):
    idOferta = IntField(required=True)
    monto = DecimalField(precision=2, required=True)
    tipo = StringField(max_length=100, required=True)
    tasa = DecimalField(precision=2, required=True)
    franquicia = StringField(max_length=100, required=True)
    descripcion = StringField(required=True)

class SolicitudEmbebida(EmbeddedDocument):
    idSolicitud = IntField(required=True)
    estado = StringField(required=True)
    ofertas = ListField(EmbeddedDocumentField('Oferta'))

class Solicitud(Document):
    idSolicitud = IntField(required=True)
    estado = StringField(required=True)
    idCliente = IntField(required=True)
    ofertas = ListField(EmbeddedDocumentField('Oferta'))


class SolicitudesRecientes(Document):
    solicitudes = ListField(EmbeddedDocumentField('SolicitudEmbebida'))
    idCliente = IntField(required=True)
    cantidadSolicitudes = IntField()

class Contador(Document):
    idSolicitud = IntField(required=True)
    






