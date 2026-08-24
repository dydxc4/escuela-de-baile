from rest_framework import viewsets, parsers
from .serializers import *

class TipoDocumentoViewSet(viewsets.ModelViewSet):
    serializer_class = TipoDocumentoSerializer
    queryset = TipoDocumento.objects.all()

class SalarioViewSet(viewsets.ModelViewSet):
    serializer_class = SalarioSerializer
    queryset = Salario.objects.all()

class EstudianteViewSet(viewsets.ModelViewSet):
    queryset = Estudiante.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return EstudianteListSerializer
        return EstudianteSerializer

class TutorViewSet(viewsets.ModelViewSet):
    queryset = Tutor.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return TutorListSerializer
        return TutorSerializer

class InstructorViewSet(viewsets.ModelViewSet):
    queryset = Instructor.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return InstructorListSerializer
        elif self.action == 'retrieve':
            return InstructorReadSerializer
        return InstructorWriteSerializer

class TutorEstudianteViewSet(viewsets.ModelViewSet):
    queryset = TutorEstudiante.objects.all()

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return TutorEstudianteReadSerializer
        return TutorEstudianteWriteSerializer

class CursoViewSet(viewsets.ModelViewSet):
    serializer_class = CursoSerializer
    queryset = Curso.objects.all()

class PeriodoViewSet(viewsets.ModelViewSet):
    serializer_class = PeriodoSerializer
    queryset = Periodo.objects.all()

class ClaseViewSet(viewsets.ModelViewSet):
    queryset = Clase.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return ClaseListSerializer
        elif self.action == 'retrieve':
            return ClaseReadSerializer
        return ClaseWriteSerializer

class CuotaViewSet(viewsets.ModelViewSet):
    queryset = Cuota.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return CuotaListSerializer
        elif self.action == 'retrieve':
            return CuotaReadSerializer
        return CuotaWriteSerializer

class PagoEstudianteViewSet(viewsets.ModelViewSet):
    queryset = PagoEstudiante.objects.all()

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

    def get_serializer_class(self):
        if self.action == 'list':
            return PagoInstructorListSerializer
        elif self.action == 'retrieve':
            return PagoInstructorReadSerializer
        elif self.action == 'create':
            return PagoInstructorCreateSerializer
        return PagoInstructorUpdateSerializer

class DocumentoViewSet(viewsets.ModelViewSet):
    queryset = Documento.objects.all()
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return DocumentoReadSerializer
        elif self.action == 'create':
            return DocumentoCreateSerializer
        return DocumentoUpdateSerializer
