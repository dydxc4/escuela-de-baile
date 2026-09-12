from django.utils import timezone
from datetime import timedelta, date
from django.db.models import F, Sum, Count, Avg, Value
from django.db.models.functions import Concat
from .models import PagoEstudiante, PagoInstructor

def generar_datos_reporte_semanal():
    # Define el rango de fechas (últimos 7 días a partir de la fecha de inicio)
    hoy = timezone.now().date()
    inicio_semana = hoy - timedelta(days=7)
    rango_fechas = (inicio_semana, hoy)

    # Filtra los querysets base
    ventas_semana = PagoEstudiante.objects \
        .filter(fecha_registro__date__range=rango_fechas) \
        .annotate(
            nombre_estudiante=Concat(
                F('estudiante__nombre'), Value(' '),
                F('estudiante__apellido_paterno'), Value(' '),
                F('estudiante__apellido_materno')
            )
        )
    salarios_semana = PagoInstructor.objects \
        .filter(fecha_registro__date__range=rango_fechas, esta_confirmado=True) \
        .annotate(
            nombre_instructor=Concat(
                F('instructor__nombre'), Value(' '),
                F('instructor__apellido_paterno'), Value(' '),
                F('instructor__apellido_materno')
            )
        )

    # Obtiene las métricas de Ingresos Realizados
    ingresos = ventas_semana.filter(estado='COMPLETADO').aggregate(
        ingreso_total=Sum('monto', default=0),
        cantidad_ventas=Count('id'),
        ticket_promedio=Avg('monto', default=0)
    )

    # Obtiene las métricas de egresos
    egreso_total = salarios_semana.aggregate(total=Sum('monto', default=0))['total'] or 0

    # Obtiene un resumen de cobranza en tránsito
    estados_transito = ['PENDIENTE', 'POR_CONFIRMAR']
    en_transito = ventas_semana.filter(estado__in=estados_transito).aggregate(
        monto_transito=Sum('monto', default=0),
        cantidad_transito=Count('id')
    )

    # Genera alertas y excepciones
    estados_alerta = ['CANCELADO', 'DEVUELTO']
    alertas = ventas_semana.filter(estado__in=estados_alerta) \
        .values('nombre_estudiante', 'cuota__concepto', 'monto', 'estado', 'fecha_registro')

    # Obtiene las ventas efectuados
    ventas_efectuadas = ventas_semana.filter(estado='COMPLETADO') \
        .values('nombre_estudiante', 'cuota__concepto', 'monto', 'fecha_registro') \
        .order_by('-fecha_registro')

    # Obtiene los salarios efectuados
    salarios_efectuados = salarios_semana \
        .values('nombre_instructor', 'salario__concepto', 'monto', 'fecha_registro') \
        .order_by('-fecha_registro')

    # Obtiene las métricas de perdidas
    perdidas = ventas_semana.filter(estado__in=estados_alerta).values('estado').annotate(
        total=Sum('monto', default=0),
        cantidad=Count('id')
    )

    # . Empaquetar todo en un diccionario
    return {
        'rango': f'{inicio_semana} al {hoy}',
        'resumen': {
            'cantidad_ventas': ingresos['cantidad_ventas'] or 0,
            'ingreso_total': ingresos['ingreso_total'] or 0,
            'egreso_total': egreso_total,
            'balance_neto': (ingresos['ingreso_total'] or 0) - egreso_total,
            'ticket_promedio': round(ingresos['ticket_promedio'] or 0, 2),
        },
        'ventas': list(ventas_efectuadas),
        'salarios': list(salarios_efectuados),
        'alertas': list(alertas),
        'perdidas': list(perdidas),
        'en_transito': en_transito,
    }

def generar_datos_reporte_mensual(anio, mes):
    # Filtra registros del mes específico
    ventas_mes = PagoEstudiante.objects.filter(fecha_registro__year=anio, fecha_registro__month=mes)
    salarios_mes = PagoInstructor.objects \
        .filter(fecha_registro__year=anio, fecha_registro__month=mes) \
        .annotate(
            nombre_instructor=Concat(
                F('instructor__nombre'), Value(' '),
                F('instructor__apellido_paterno'), Value(' '),
                F('instructor__apellido_materno')
            )
        )

    # Rendimiento Global
    ingreso_global = ventas_mes.filter(estado='COMPLETADO') \
        .aggregate(total=Sum('monto', default=0))['total'] or 0
    egreso_global = salarios_mes.filter(esta_confirmado=True) \
        .aggregate(total=Sum('monto', default=0))['total'] or 0

    # Desglose de Ingresos por Concepto
    ingresos_por_concepto = ventas_mes.filter(estado='COMPLETADO') \
        .values('cuota__concepto',) \
        .annotate(total_recaudado=Sum('monto', default=0)) \
        .order_by('-total_recaudado')

    # Desglose de Nómina
    nomina_desglosada = salarios_mes \
        .values('nombre_instructor', 'salario__concepto') \
        .annotate(total_pagado=Sum('monto', default=0)) \
        .order_by('nombre_instructor')

    # Efectividad de Cobro
    total_intentos = ventas_mes.count()
    total_exitosos = ventas_mes.filter(estado='COMPLETADO').count()
    efectividad = (total_exitosos / total_intentos * 100) if total_intentos > 0 else 0

    # Empaquetar datos
    return {
        'periodo': f'{mes:02}/{anio}',
        'resumen': {
            'ingreso_global': ingreso_global,
            'egreso_global': egreso_global,
            'balance': ingreso_global - egreso_global,
            'efectividad_porcentaje': round(efectividad, 2)
        },
        'desglose_ingresos': list(ingresos_por_concepto),
        'desglose_nomina': list(nomina_desglosada)
    }
