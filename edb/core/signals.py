from django.db.models import Sum, Q
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from dateutil.relativedelta import relativedelta
from .models import *

def increment_contador(estudiante: Estudiante, incremento):
    estudiante.contador_clases_restantes+=incremento
    estudiante.estado_inscripcion = Estudiante.Estado.ACTIVO
    estudiante.save(update_fields=['contador_clases_restantes', 'estado_inscripcion'])

def set_mensualidad(pago: PagoEstudiante):
    hoy = timezone.now().date()
    anterior = MensualidadPagada.objects \
        .filter(estudiante=pago.estudiante) \
        .order_by('-fecha_vigencia').first()
    fecha_vigencia = (anterior.fecha_vigencia if anterior else hoy) + relativedelta(months=1)
    estudiante = pago.estudiante

    MensualidadPagada.objects.create(
        pago=pago,
        estudiante=estudiante,
        fecha_vigencia=fecha_vigencia,
    )
    estudiante.estado_inscripcion = Estudiante.Estado.ACTIVO
    estudiante.save(update_fields=['estado_inscripcion'])

@receiver(post_save, sender=PagoEstudiante)
def update_contador_clases_trigger(sender, instance: PagoEstudiante, **kwargs):
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

@receiver(post_save, sender=ClaseEstudiante)
def substract_contador_clases_trigger(sender, instance: ClaseEstudiante, **kwargs):
    estudiante = instance.estudiante
    if not estudiante.esta_al_corriente and estudiante.contador_clases_restantes > 0 and instance.asistio:
        estudiante.contador_clases_restantes-=1
        estudiante.save(update_fields=['contador_clases_restantes'])
