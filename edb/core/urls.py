from django.urls import path, include
from rest_framework import urls
from rest_framework.routers import DefaultRouter
from .viewsets import *

router = DefaultRouter()

router.register(r'tipos_documentos', TipoDocumentoViewSet, basename='tipo_documento')
router.register(r'salarios', SalarioViewSet, basename='salario')
router.register(r'estudiantes', EstudianteViewSet, basename='estudiante')
router.register(r'tutores', TutorViewSet, basename='tutor')
router.register(r'instructores', InstructorViewSet, basename='instructor')
router.register(r'tutores_estudiantes', TutorEstudianteViewSet, basename='tutor_estudiante')
router.register(r'cursos', CursoViewSet, basename='curso')
router.register(r'clases', ClaseViewSet, basename='clase')
router.register(r'clases_estudiantes', ClaseEstudianteViewSet, basename='clase_estudiante')
router.register(r'cuotas', CuotaViewSet, basename='cuota')
router.register(r'pago_estudiantes', PagoEstudianteViewSet, basename='pago_estudiante')
router.register(r'pago_instructores', PagoInstructorViewSet, basename='pago_instructor')
router.register(r'documentos', DocumentoViewSet, basename='documento')
router.register(r'alertas_estudiantes', AlertaEstudianteViewSet, basename='alerta_estudiante')

urlpatterns = [
    path('', include(router.urls)),
    path('registros', RegistroDiarioListView.as_view(), name='registros'),
    path('registros/hoy', RegistroDiarioReadView.as_view(), name='registros_hoy'),
    path('registros/semana', RegistroSemanalView.as_view(), name='registros_semana'),
    path('registros/mes', RegistroMensualView.as_view(), name='registros_mes'),
    path('configuracion', ConfiguracionView.as_view(), name='configuracion'),
]
