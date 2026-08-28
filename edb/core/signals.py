import os
from dateutil.relativedelta import relativedelta
from django.db.models import Sum, Q
from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from .models import *

def increment_contador(estudiante: Estudiante, incremento):
    estudiante.contador_clases_restantes+=incremento
    estudiante.estado_inscripcion = Estudiante.Estado.ACTIVO
    estudiante.save(update_fields=['contador_clases_restantes', 'estado_inscripcion'])

def set_mensualidad(pago: PagoEstudiante):
    hoy = timezone.now().date()
    estudiante = pago.estudiante
    anterior = MensualidadPagada.objects \
        .filter(estudiante=pago.estudiante, fecha_vigencia__gte=hoy) \
        .order_by('-fecha_vigencia') \
        .first()
    fecha_vigencia = (anterior.fecha_vigencia if anterior else hoy) + \
        relativedelta(months=1)

    MensualidadPagada.objects.create(
        pago=pago,
        estudiante=estudiante,
        fecha_vigencia=fecha_vigencia,
    )
    estudiante.estado_inscripcion = Estudiante.Estado.ACTIVO
    estudiante.save(update_fields=['estado_inscripcion'])

@receiver(pre_save, sender=PagoEstudiante)
@receiver(pre_save, sender=PagoInstructor)
def update_registro_transacciones_trigger(sender, instance, **kwargs):
    if instance.pk is None:
        registro = RegistroDiario.load()
        registro.cantidad_transacciones += 1
        registro.save(update_fields=['cantidad_transacciones'])

@receiver(post_save, sender=PagoInstructor)
def update_registro_salarios_trigger(sender, instance: PagoInstructor, **kwargs):
    if instance.esta_confirmado:
        registro = RegistroDiario.load()
        registro.egreso_total = instance.monto
        registro.cantidad_salarios += 1
        registro.save(update_fields=['egreso_total', 'cantidad_salarios', 'ganancia_total'])

@receiver(post_save, sender=PagoEstudiante)
def update_contador_clases_trigger(sender, instance: PagoEstudiante, **kwargs):
    # Obtiene el registro de la fecha actual
    registro = RegistroDiario.load()

    # Si se marca el pago como completado
    if instance.estado == PagoEstudiante.Estado.COMPLETADO:
        estudiante = instance.estudiante
        # Si se pago por una clase individual
        if instance.cuota.tipo == Cuota.Tipo.CLASE_INDIVIDUAL:
            increment_contador(estudiante, 1)
        # Si se pago por un paquete de clases
        elif instance.cuota.tipo in [Cuota.Tipo.PAQUETE_CLASES, Cuota.Tipo.INSCRIPCION] and \
            instance.cuota.cantidad_clases:
            increment_contador(estudiante, instance.cuota.cantidad_clases)
        # Si se pago por una mensualidad
        elif instance.cuota.tipo == Cuota.Tipo.MENSUALIDAD:
            set_mensualidad(instance)

        registro.ingreso_total += instance.monto
        registro.cantidad_ventas += 1
        registro.ticket_promedio = registro.ingreso_total / registro.cantidad_ventas
        registro.save(update_fields=['ingreso_total', 'cantidad_ventas', 'ticket_promedio', 'ganancia_total'])
    elif instance.estado == PagoEstudiante.Estado.DEVUELTO:
        registro.cantidad_devoluciones += 1
        registro.perdida_total += instance.monto
        registro.save(update_fields=['cantidad_devoluciones', 'perdida_total', 'ganancia_total'])
    elif instance.estado == PagoEstudiante.Estado.CANCELADO:
        registro.cantidad_cancelaciones += 1
        registro.perdida_total += instance.monto
        registro.save(update_fields=['cantidad_cancelaciones', 'perdida_total', 'ganancia_total'])

@receiver(post_save, sender=ClaseEstudiante)
def substract_contador_clases_trigger(sender, instance: ClaseEstudiante, **kwargs):
    estudiante = instance.estudiante
    if not estudiante.esta_al_corriente and estudiante.contador_clases_restantes > 0 and instance.asistio:
        estudiante.contador_clases_restantes-=1
        estudiante.save(update_fields=['contador_clases_restantes'])

@receiver(post_delete, sender=Documento)
def delete_documento_trigger(sender, instance: Documento, **kwargs):
    if instance.archivo and (instance.archivo.path):
        os.remove(instance.archivo.path)
