from django.core.mail import EmailMessage
from django.db import models
from django.db.models import functions
from django.shortcuts import render
from django.template.loader import render_to_string
from django.utils import timezone
from django.conf import settings
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from weasyprint import HTML

from .reports import *
from .models import RegistroDiario, Configuracion

# Create your views here.

def reporte_semanal_html(request):
    data = generar_datos_reporte_semanal()
    return render(request, 'reporte-semanal.html', data)

def reporte_mensual_html(request):
    hoy = timezone.now().date()
    data = generar_datos_reporte_mensual(hoy.year, hoy.month)
    return render(request, 'reporte-mensual.html', data)

def enviar_correo(asunto, cuerpo, pdf, nombre_archivo):
    origen = settings.MAILERS['default']['OPTIONS']['username']
    destinatarios = Configuracion.load().emails_destinatarios

    if len(destinatarios) == 0:
        return Response(
            {'error': 'No hay destinatarios registrados'},
            status=status.HTTP_412_PRECONDITION_FAILED
        )

    # Obtiene el destinatario
    correo = EmailMessage(
        subject=asunto,
        body=cuerpo,
        from_email=origen,
        to=destinatarios,
    )

    # Adjuntar el PDF generado en memoria
    correo.attach(filename=nombre_archivo, content=pdf, mimetype='application/pdf')

    try:
        # Enviar el correo
        correo.send()
        return Response(
            { 'mensaje': f'Reporte generado y enviado con éxito a los destinatarios registrados.'},
            status=status.HTTP_200_OK
        )
    except Exception as e:
        return Response(
            {'error': f'Ocurrió un error al enviar el correo: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

class RegistroSemanalView(APIView):
    def get(self, request):
        queryset = RegistroDiario.objects.all()
        reporte = (
            queryset
            .annotate(
                semana=functions.TruncWeek('fecha'),
            )
            .values('semana')
            .annotate(
                cantidad_ventas=models.Sum('cantidad_ventas'),
                cantidad_devoluciones=models.Sum('cantidad_devoluciones'),
                cantidad_cancelaciones=models.Sum('cantidad_cancelaciones'),
                ingresos=models.Sum('ingreso_total'),
                egresos=models.Sum('egreso_total'),
                ganancias=models.Sum('ganancia_total'),
                perdidas=models.Sum('perdida_total'),
                ticket_promedio_diario=models.Avg('ticket_promedio'),
            )
            .order_by('-semana')
        )

        return Response(reporte)

class RegistroMensualView(APIView):
    def get(self, request):
        queryset = RegistroDiario.objects.all()
        reporte = (
            queryset
            .annotate(
                mes=functions.TruncMonth('fecha'),
            )
            .values('mes')
            .annotate(
                cantidad_ventas=models.Sum('cantidad_ventas'),
                cantidad_devoluciones=models.Sum('cantidad_devoluciones'),
                cantidad_cancelaciones=models.Sum('cantidad_cancelaciones'),
                ingresos=models.Sum('ingreso_total'),
                egresos=models.Sum('egreso_total'),
                ganancias=models.Sum('ganancia_total'),
                perdidas=models.Sum('perdida_total'),
                ticket_promedio_diario=models.Avg('ticket_promedio'),
            )
            .order_by('-mes')
        )

        return Response(reporte)

class GenerarReporteSemanalView(APIView):
    def get(self, request, *args, **kwargs):
        # Obtiene los datos para el reporte
        datos = generar_datos_reporte_semanal()
        return Response(datos)

class EnviarReporteSemanalView(APIView):
    def post(self, request, *args, **kwargs):
        hoy = timezone.now().date()
        # Obtiene los datos para el reporte
        datos = generar_datos_reporte_semanal()
        # Renderiza la plantilla HTML inyectando los datos
        html_string = render_to_string('reporte-semanal.html', datos)
        # Genera el PDF en memoría
        pdf_file = HTML(string=html_string).write_pdf() or bytes()
        # Establece los datos del correo
        asunto=f'Reporte semanal - {datos['rango']}'
        cuerpo='Adjunto encontrarás el reporte semanal detallado con los indicadores clave de la escuela y el desglose de ventas.'
        nombre_archivo = f'reporte_semanal_{hoy:%Y_%m-%d}.pdf'

        return enviar_correo(asunto, cuerpo, pdf_file, nombre_archivo)

class GenerarReporteMensualView(APIView):
    def get(self, request, *args, **kwargs):
        hoy = timezone.now().date()
        datos = generar_datos_reporte_mensual(hoy.year, hoy.month)
        return Response(datos)

class EnviarReporteMensualView(APIView):
    def post(self, request, *args, **kwargs):
        # Obtiene los datos para el reporte
        hoy = timezone.now().date()
        datos = generar_datos_reporte_mensual(hoy.year, hoy.month)
        # Renderiza la plantilla HTML inyectando los datos
        html_string = render_to_string('reporte-mensual.html', datos)
        # Genera el PDF en memoría
        pdf_file = HTML(string=html_string).write_pdf() or bytes()

        asunto = f'Reporte Mensual - {datos['periodo']}'
        cuerpo = 'Adjunto encontrarás el reporte mensual detallado con los indicadores clave de la escuela.'
        nombre_archivo = f'reporte_mensual_{hoy.month:02}_{hoy.year}.pdf'

        return enviar_correo(asunto, cuerpo, pdf_file, nombre_archivo)
