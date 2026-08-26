from rest_framework.permissions import BasePermission
from .models import *

class EsCuotaPagadaAlterable(BasePermission):
    message = 'No es posible alterar una cuota de un pago finalizado'

    def has_object_permission(self, request, view, obj: CuotaPagada):
        if request.method in ['DELETE', 'PUT', 'PATCH']:
            return not obj.pago.estado.es_finalizado()
        return True

class EsPagoEstudianteAlterable(BasePermission):
    message = 'No es posible alterar un pago finalizado'

    def has_object_permission(self, request, view, obj: PagoEstudiante):
        if request.method in ['DELETE', 'PUT', 'PATCH']:
            return not obj.estado.es_finalizado()
        return True

class EsPagoInstructorAlterable(BasePermission):
    message = 'No es posible alterar un pago finalizado'

    def has_object_permission(self, request, view, obj: PagoInstructor):
        if request.method in ['DELETE', 'PUT', 'PATCH']:
            return not obj.esta_confirmado
        return True

class EsClaseAlterable(BasePermission):
    message = 'No es posible alterar una clase completada'

    def has_object_permission(self, request, view, obj: Clase):
        if request.method in ['DELETE', 'PUT', 'PATCH']:
            return not obj.estado == Clase.Estado.COMPLETADA
        return True

class EsClaseEstudianteAlterable(BasePermission):
    message = 'No es posible alterar una asistencia a una clase'

    def has_object_permission(self, request, view, obj: ClaseEstudiante):
        if request.method in ['DELETE', 'PUT', 'PATCH']:
            return not (obj.clase.estado == Clase.Estado.COMPLETADA or obj.asistio)
        return True
