from rest_framework import serializers
from .models import *

class TipoDocumentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoDocumento
        fields = '__all__'

class SalarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Salario
        fields = '__all__'

class TutorListSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Tutor
        fields = [
            'id',
            'nombre_completo',
            'correo_electronico',
            'telefono'
        ]

    def get_nombre_completo(self, obj: Tutor):
        return f'{obj}'

class TutorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tutor
        fields = '__all__'

class EstudianteListSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Estudiante
        fields = [
            'id',
            'nombre_completo',
            'genero',
            'curp',
            'estado_inscripcion',
            'fecha_registro',
        ]

    def get_nombre_completo(self, obj: Estudiante):
        return f'{obj}'

class EstudianteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estudiante
        fields = '__all__'

class InstructorListSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Instructor
        fields = [
            'id',
            'nombre_completo',
            'correo_electronico',
            'telefono',
            'esta_habilitado'
        ]

    def get_nombre_completo(self, obj: Tutor):
        return f'{obj}'

class InstructorReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Instructor
        fields = '__all__'
        depth = 1

class InstructorWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Instructor
        fields = '__all__'

class TutorEstudianteReadSerializer(serializers.ModelSerializer):
    estudiante = EstudianteListSerializer(read_only=True)
    tutor = TutorListSerializer(read_only=True)

    class Meta:
        model = TutorEstudiante
        fields = '__all__'
        depth = 1

class TutorEstudianteWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = TutorEstudiante
        fields = '__all__'

class CursoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Curso
        fields = '__all__'

class PeriodoSerializer(serializers.ModelSerializer):
    nombre_curso = serializers.CharField(source='curso.nombre', read_only=True)

    class Meta:
        model = Periodo
        fields = '__all__'

class ClaseListSerializer(serializers.ModelSerializer):
    nombre_instructor = serializers.SerializerMethodField(read_only=True)
    curso = serializers.PrimaryKeyRelatedField(source='periodo.curso', read_only=True)
    nombre_curso = serializers.CharField(source='periodo.curso.nombre', read_only=True)
    fechas_periodo = serializers.SerializerMethodField(read_only=True)
    cantidad_estudiantes = serializers.IntegerField(read_only=True)

    class Meta:
        model = Clase
        exclude = ['estudiantes']

    def get_fechas_periodo(self, obj: Clase):
        return f'{obj.periodo.fecha_inicio} - {obj.periodo.fecha_finalizacion}'

    def get_nombre_instructor(self, obj: Clase):
        return f'{obj.instructor}'

class ClaseReadSerializer(serializers.ModelSerializer):
    estudiantes = EstudianteListSerializer(many=True, read_only=True)
    instructor = InstructorListSerializer(read_only=True)
    periodo = PeriodoSerializer(read_only=True)

    class Meta:
        model = Clase
        fields = '__all__'
        depth = 1

class ClaseWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clase
        fields = '__all__'

class CuotaListSerializer(serializers.ModelSerializer):
    fechas_periodo = serializers.SerializerMethodField(read_only=True)
    curso = serializers.PrimaryKeyRelatedField(source='periodo.curso', read_only=True)
    nombre_curso = serializers.CharField(source='periodo.curso.nombre', read_only=True)
    cantidad_clases = serializers.IntegerField(read_only=True)

    class Meta:
        model = Cuota
        exclude = [
            'fecha_registro',
            'fecha_actualizacion',
            'clases'
        ]

    def get_fechas_periodo(self, obj: Cuota):
        if obj.periodo is not None:
            return f'{obj.periodo.fecha_inicio} - {obj.periodo.fecha_finalizacion}'
        return None

class CuotaReadSerializer(serializers.ModelSerializer):
    clases = ClaseListSerializer(many=True, read_only=True)
    periodo = PeriodoSerializer(read_only=True)

    class Meta:
        model = Cuota
        fields = '__all__'
        depth = 1

class CuotaWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cuota
        fields = '__all__'

class PagoEstudianteListSerializer(serializers.ModelSerializer):
    nombre_estudiante = serializers.SerializerMethodField(read_only=True)
    cantidad_cuotas = serializers.IntegerField(read_only=True)

    class Meta:
        model = PagoEstudiante
        exclude = ['cuotas']

    def get_nombre_estudiante(self, obj: PagoEstudiante):
        return f'{obj.estudiante}'

class PagoEstudianteReadSerializer(serializers.ModelSerializer):
    estudiante = EstudianteListSerializer(read_only=True)
    cuotas = CuotaListSerializer(many=True, read_only=True)

    class Meta:
        model = PagoEstudiante
        fields = '__all__'
        depth = 1

class PagoEstudianteCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PagoEstudiante
        exclude = ['total']
        read_only_fields = ['total']

class PagoEstudianteUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PagoEstudiante
        exclude = ['estudiante', 'total']
        read_only_fields = ['estudiante', 'total']

class PagoInstructorListSerializer(serializers.ModelSerializer):
    nombre_instructor = InstructorListSerializer(read_only=True)
    concepto_salario = serializers.CharField(source='salario.concepto', read_only=True)

    class Meta:
        model = PagoInstructor
        fields = '__all__'

    def get_nombre_instructor(self, obj: PagoInstructor):
        return f'{obj.instructor}'

class PagoInstructorReadSerializer(serializers.ModelSerializer):
    instructor = InstructorListSerializer(read_only=True)

    class Meta:
        model = PagoInstructor
        fields = '__all__'
        depth = 1

class PagoInstructorCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PagoInstructor
        exclude = ['monto']
        read_only_fields = ['monto']

class PagoInstructorUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PagoInstructor
        exclude = ['instructor', 'monto']
        read_only_fields = ['instructor', 'monto']

class DocumentoReadSerializer(serializers.ModelSerializer):
    tamanio = serializers.SerializerMethodField()
    tipo_archivo = serializers.SerializerMethodField()
    estudiante = EstudianteListSerializer(read_only=True)
    instructor = InstructorListSerializer(read_only=True)
    pago = PagoEstudianteListSerializer(read_only=True)

    class Meta:
        model = Documento
        fields = '__all__'
        depth = 1

    def get_tamanio(self, obj):
        return obj.archivo.size

    def get_tipo_archivo(self, obj):
        return obj.archivo.name.split('.')[-1].lower()

class DocumentoCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Documento
        fields = '__all__'

    def validate(self, attrs: dict):
        counter = 0
        counter += 'estudiante' in attrs
        counter += 'instructor' in attrs
        counter += 'pago' in attrs

        if counter == 0:
            raise serializers.ValidationError({
                'message': 'Debe establecer un identificador de estudiante, instructor o pago.'
                }
            )
        if counter > 1:
            raise serializers.ValidationError({
                'message': 'No se pueden establecer más de un identificador de estudiante, instructor o pago al mismo tiempo.'
                }
            )

        return attrs

class DocumentoUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Documento
        fields = ['tipo', 'notas']
        read_only_fields = ['id', 'estudiante', 'instructor', 'pago', 'archivo']
