from rest_framework import viewsets, parsers
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import *
from .filters import *

class TipoDocumentoViewSet(viewsets.ModelViewSet):
    serializer_class = TipoDocumentoSerializer
    queryset = TipoDocumento.objects.all()
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['nombre']
    ordering_fields = ['nombre']
    ordering = ['nombre']

class SalarioViewSet(viewsets.ModelViewSet):
    serializer_class = SalarioSerializer
    queryset = Salario.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = SalarioFilter
    search_fields = ['concepto']
    ordering_fields = ['monto', 'fecha_registro']
    ordering = ['-fecha_registro']

class EstudianteViewSet(viewsets.ModelViewSet):
    queryset = Estudiante.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = EstudianteFilter
    search_fields = [
        'nombre',
        'apellido_paterno',
        'apellido_materno',
        'correo_electronico',
        'telefono',
        'curp',
    ]
    ordering_fields = [
        'apellido_paterno',
        'apellido_materno',
        'nombre',
        'correo_electronico',
        'telefono',
        'curp',
        'fecha_nacimiento',
        'fecha_registro',
    ]
    ordering = ['nombre', 'apellido_paterno', 'apellido_materno']

    def get_serializer_class(self):
        if self.action == 'list':
            return EstudianteListSerializer
        return EstudianteSerializer

class TutorViewSet(viewsets.ModelViewSet):
    queryset = Tutor.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = TutorFilter
    search_fields = [
        'nombre',
        'apellido_paterno',
        'apellido_materno',
        'correo_electronico',
        'telefono',
    ]
    ordering_fields = [
        'apellido_paterno',
        'apellido_materno',
        'nombre',
        'correo_electronico',
        'telefono',
        'fecha_registro',
    ]
    ordering = ['nombre', 'apellido_paterno', 'apellido_materno']

    def get_serializer_class(self):
        if self.action == 'list':
            return TutorListSerializer
        return TutorSerializer

class InstructorViewSet(viewsets.ModelViewSet):
    queryset = Instructor.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = InstructorFilter
    search_fields = [
        'nombre',
        'apellido_paterno',
        'apellido_materno',
        'correo_electronico',
        'telefono',
    ]
    ordering_fields = [
        'apellido_paterno',
        'apellido_materno',
        'nombre',
        'correo_electronico',
        'telefono',
        'fecha_registro',
    ]
    ordering = ['nombre', 'apellido_paterno', 'apellido_materno']

    def get_serializer_class(self):
        if self.action == 'list':
            return InstructorListSerializer
        elif self.action == 'retrieve':
            return InstructorReadSerializer
        return InstructorWriteSerializer

class TutorEstudianteViewSet(viewsets.ModelViewSet):
    queryset = TutorEstudiante.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_class = TutorEstudianteFilter

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return TutorEstudianteReadSerializer
        return TutorEstudianteWriteSerializer

class CursoViewSet(viewsets.ModelViewSet):
    serializer_class = CursoSerializer
    queryset = Curso.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = CursoFilter
    search_fields = ['nombre', 'descripcion']
    ordering_fields = ['nombre', 'fecha_creacion']
    ordering = ['-fecha_creacion']

class PeriodoViewSet(viewsets.ModelViewSet):
    serializer_class = PeriodoSerializer
    queryset = Periodo.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = PeriodoFilter
    search_fields = ['curso__nombre', 'curso__descripcion']
    ordering_fields = ['fecha_inicio', 'fecha_finalizacion']
    ordering = ['fecha_inicio']

class ClaseViewSet(viewsets.ModelViewSet):
    queryset = Clase.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ClaseFilter
    search_fields = [
        'descripcion',
        'periodo__curso__nombre',
        'instructor__nombre',
        'instructor__apellido_paterno',
        'instructor__apellido_materno',
    ]
    ordering_fields = ['fecha_hora']
    ordering = ['fecha_hora']

    def get_serializer_class(self):
        if self.action == 'list':
            return ClaseListSerializer
        elif self.action == 'retrieve':
            return ClaseReadSerializer
        return ClaseWriteSerializer

class ClaseEstudianteViewSet(viewsets.ModelViewSet):
    queryset = ClaseEstudiante.objects.all()
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = ClaseEstudianteFilter
    ordering_fields = [
        'estudiante__nombre',
        'estudiante__apellido_paterno',
        'estudiante__apellido_materno',
        'fecha_registro',
    ]
    ordering = [
        'estudiante__nombre',
        'estudiante__apellido_paterno',
        'estudiante__apellido_materno',
    ]

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return ClaseEstudianteReadSerializer
        elif self.action == 'create':
            return ClaseEstudianteCreateSerializer
        return ClaseEstudianteUpdateSerializer

class CuotaViewSet(viewsets.ModelViewSet):
    queryset = Cuota.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = CuotaFilter
    search_fields = [
        'concepto',
        'periodo__curso__nombre',
    ]
    ordering_fields = ['costo', 'fecha_limite', 'fecha_registro']
    ordering = ['-fecha_registro']

    def get_serializer_class(self):
        if self.action == 'list':
            return CuotaListSerializer
        elif self.action == 'retrieve':
            return CuotaReadSerializer
        elif self.action == 'create':
            return CuotaCreateSerializer
        return CuotaUpdateSerializer

class PagoEstudianteViewSet(viewsets.ModelViewSet):
    queryset = PagoEstudiante.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = PagoEstudianteFilter
    search_fields = [
        'estudiante__nombre',
        'estudiante__apellido_paterno',
        'estudiante__apellido_materno',
    ]
    ordering_fields = ['total', 'fecha_confirmacion', 'fecha_registro']
    ordering = ['-fecha_registro']

    def get_serializer_class(self):
        if self.action == 'list':
            return PagoEstudianteListSerializer
        elif self.action == 'retrieve':
            return PagoEstudianteReadSerializer
        elif self.action == 'create':
            return PagoEstudianteCreateSerializer
        return PagoEstudianteUpdateSerializer

class PagoInstructorViewSet(viewsets.ModelViewSet):
    queryset = PagoInstructor.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = PagoInstructorFilter
    search_fields = [
        'salario__concepto'
        'instructor__nombre',
        'instructor__apellido_paterno',
        'instructor__apellido_materno',
    ]
    ordering_fields = ['monto', 'fecha_registro']
    ordering = ['-fecha_registro']

    def get_serializer_class(self):
        if self.action == 'list':
            return PagoInstructorListSerializer
        elif self.action == 'retrieve':
            return PagoInstructorReadSerializer
        elif self.action == 'create':
            return PagoInstructorCreateSerializer
        return PagoInstructorUpdateSerializer

class CuotaPagadaViewSet(viewsets.ModelViewSet):
    queryset = CuotaPagada.objects.all()
    http_method_names = ['get', 'post', 'delete', 'head', 'options']
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = CuotaPagadaFilter
    search_fields = [
        'cuota__concepto'
        'pago__estudiante__nombre',
        'pago__estudiante__apellido_paterno',
        'pago__estudiante__apellido_materno',
    ]
    ordering_fields = ['monto', 'pago__fecha_registro']
    ordering = ['-pago__fecha_registro']

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return CuotaPagadaReadSerializer
        return CuotaPagadaWriteSerializer

class DocumentoViewSet(viewsets.ModelViewSet):
    queryset = Documento.objects.all()
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = DocumentoFilter
    search_fields = [
        'notas',
    ]
    ordering_fields = ['fecha_subida']
    ordering = ['-fecha_subida']

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return DocumentoReadSerializer
        elif self.action == 'create':
            return DocumentoCreateSerializer
        return DocumentoUpdateSerializer
