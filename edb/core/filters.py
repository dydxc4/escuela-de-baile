import django_filters
from .models import *

class SalarioFilter(django_filters.FilterSet):
    class Meta:
        model = Salario
        fields = {
            'monto': ['lte', 'gte'],
            'esta_habilitado': ['exact'],
        }

class EstudianteFilter(django_filters.FilterSet):
    class Meta:
        model = Estudiante
        fields = {
            'genero': ['exact', 'isnull'],
            'estado_inscripcion': ['exact'],
            'posee_tarjeta_asistencia': ['exact'],
            'fecha_nacimiento': ['year__lte', 'year__gte', 'year__exact'],
            #'edad': ['lte', 'gte', 'exact'],
            'fecha_registro': ['date__lte', 'date__gte', 'date__exact'],
        }

class TutorFilter(django_filters.FilterSet):
    class Meta:
        model = Tutor
        fields = {
            'fecha_registro': ['date__lte', 'date__gte', 'date__exact'],
        }

class InstructorFilter(django_filters.FilterSet):
    salario = django_filters.ModelChoiceFilter(queryset=Salario.objects.all())
    salario__lte = django_filters.NumberFilter(field_name='salario__monto', lookup_expr='lte')
    salario__gte = django_filters.NumberFilter(field_name='salario__monto', lookup_expr='gte')

    class Meta:
        model = Instructor
        fields = {
            'esta_habilitado': ['exact'],
            'fecha_registro': ['date__lte', 'date__gte', 'date__exact'],
        }

class TutorEstudianteFilter(django_filters.FilterSet):
    tutor = django_filters.ModelChoiceFilter(queryset=Tutor.objects.all())
    estudiante = django_filters.ModelChoiceFilter(queryset=Estudiante.objects.all())

    class Meta:
        model = TutorEstudiante
        fields = {
            'parentesco': ['exact'],
        }

class CursoFilter(django_filters.FilterSet):
    class Meta:
        model = Curso
        fields = {
            'esta_habilitado': ['exact'],
            'fecha_creacion': ['date__lte', 'date__gte', 'date__exact'],
        }
class PeriodoFilter(django_filters.FilterSet):
    curso = django_filters.ModelChoiceFilter(queryset=Curso.objects.all())

    class Meta:
        model = Periodo
        fields = {
            'fecha_inicio': ['gte', 'lte', 'exact'],
            'fecha_finalizacion': ['gte', 'lte', 'exact'],
            'curso__esta_habilitado': ['exact'],
        }


class ClaseFilter(django_filters.FilterSet):
    instructor = django_filters.ModelChoiceFilter(queryset=Instructor.objects.all())
    curso = django_filters.ModelChoiceFilter(field_name='periodo__curso', queryset=Curso.objects.all())
    periodo = django_filters.ModelChoiceFilter(queryset=Periodo.objects.all())

    class Meta:
        model = Clase
        fields = {
            'fecha_hora': ['date__lte', 'date__gte', 'date__exact'],
            'estado': ['exact'],
        }

class ClaseEstudianteFilter(django_filters.FilterSet):
    clase = django_filters.ModelChoiceFilter(queryset=Clase.objects.all())
    estudiante = django_filters.ModelChoiceFilter(queryset=Estudiante.objects.all())
    instuctor = django_filters.ModelChoiceFilter(field_name='clase__instructor', queryset=Instructor.objects.all())
    curso = django_filters.ModelChoiceFilter(field_name='clase__periodo__curso', queryset=Curso.objects.all())
    periodo = django_filters.ModelChoiceFilter(field_name='clase__periodo', queryset=Periodo.objects.all())

    class Meta:
        model = ClaseEstudiante
        fields = {
            'asistio': ['exact'],
            'fecha_registro': ['date__lte', 'date__gte', 'date__exact'],
        }

class CuotaFilter(django_filters.FilterSet):
    curso = django_filters.ModelChoiceFilter(field_name='periodo__curso', queryset=Curso.objects.all())
    periodo = django_filters.ModelChoiceFilter(queryset=Periodo.objects.all())

    class Meta:
        model = Cuota
        fields = {
            'tipo': ['exact'],
            'costo': ['lte', 'gte', 'exact'],
            'fecha_limite': ['lte', 'gte', 'exact'],
            'esta_habilitado': ['exact'],
            'fecha_registro': ['lte', 'gte', 'exact'],
        }

class PagoEstudianteFilter(django_filters.FilterSet):
    estudiante = django_filters.ModelChoiceFilter(queryset=Estudiante.objects.all())

    class Meta:
        model = PagoEstudiante
        fields = {
            'estado': ['exact'],
            'total': ['lte', 'gte', 'exact'],
            'fecha_confirmacion': ['date__lte', 'date__gte', 'date__exact'],
            'fecha_registro': ['date__lte', 'date__gte', 'date__exact'],
        }

class PagoInstructorFilter(django_filters.FilterSet):
    instructor = django_filters.ModelChoiceFilter(queryset=Instructor.objects.all())
    salario = django_filters.ModelChoiceFilter(queryset=Salario.objects.all())

    class Meta:
        model = PagoInstructor
        fields = {
            'esta_confirmado': ['exact'],
            'monto': ['lte', 'gte', 'exact'],
            'fecha_registro': ['date__lte', 'date__gte', 'date__exact'],
        }

class CuotaPagadaFilter(django_filters.FilterSet):
    cuota = django_filters.ModelChoiceFilter(queryset=Cuota.objects.all())
    pago = django_filters.ModelChoiceFilter(queryset=PagoEstudiante.objects.all())
    estudiante = django_filters.ModelChoiceFilter(field_name='pago__estudiante', queryset=Estudiante.objects.all())
    curso = django_filters.ModelChoiceFilter(field_name='pago__periodo__curso', queryset=Curso.objects.all())
    periodo = django_filters.ModelChoiceFilter(field_name='pago__periodo', queryset=Periodo.objects.all())

    class Meta:
        model = CuotaPagada
        fields = {
            'cuota__tipo': ['exact'],
            'pago__estado': ['exact'],
            'monto': ['lte', 'gte', 'exact'],
        }

class DocumentoFilter(django_filters.FilterSet):
    estudiante = django_filters.ModelChoiceFilter(queryset=Estudiante.objects.all())
    instructor = django_filters.ModelChoiceFilter(queryset=Instructor.objects.all())
    pago = django_filters.ModelChoiceFilter(queryset=PagoEstudiante.objects.all())
    tipo = django_filters.ModelChoiceFilter(queryset=TipoDocumento.objects.all())

    class Meta:
        model = Documento
        fields = {
            'fecha_subida': ['date__lte', 'date__gte', 'date__exact']
        }
