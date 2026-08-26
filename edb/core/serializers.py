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
    class Meta:
        model = Tutor
        fields = [
            'id',
            'nombre_completo',
            'correo_electronico',
            'telefono',
            'fecha_registro',
        ]

class TutorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tutor
        fields = '__all__'

class EstudianteListSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.CharField(read_only=True)
    edad = serializers.IntegerField(read_only=True)
    rango_edad = EnumField(Estudiante.RangoEdad)

    class Meta:
        model = Estudiante
        fields = [
            'id',
            'nombre_completo',
            'edad',
            'rango_edad',
            'genero',
            'curp',
            'estado_inscripcion',
            'fecha_registro',
            'contador_clases_restantes',
        ]

class EstudianteSerializer(serializers.ModelSerializer):
    edad = serializers.IntegerField(read_only=True)
    rango_edad = serializers.CharField(read_only=True)

    class Meta:
        model = Estudiante
        fields = '__all__'
        read_only_fields = ['contador_clases_restantes']

class InstructorListSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.CharField(read_only=True)

    class Meta:
        model = Instructor
        fields = [
            'id',
            'nombre_completo',
            'correo_electronico',
            'telefono',
            'esta_habilitado',
            'fecha_registro',
        ]

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

class ClaseEstudianteListSerializer(serializers.ModelSerializer):
    estudiante = EstudianteListSerializer(read_only=True)

    class Meta:
        model = ClaseEstudiante
        exclude = ['clase']
        depth = 1

class ClaseListSerializer(serializers.ModelSerializer):
    nombre_instructor = serializers.CharField(source='instructor.nombre_completo', read_only=True)
    nombre_curso = serializers.CharField(source='curso.nombre', read_only=True)
    cantidad_estudiantes = serializers.IntegerField(read_only=True)

    class Meta:
        model = Clase
        exclude = ['estudiantes']

class ClaseReadSerializer(serializers.ModelSerializer):
    estudiantes = ClaseEstudianteListSerializer(source='estudiantes_clase', many=True, read_only=True)
    instructor = InstructorListSerializer(read_only=True)

    class Meta:
        model = Clase
        fields = '__all__'
        depth = 1

class ClaseWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clase
        fields = '__all__'

class ClaseEstudianteReadSerializer(serializers.ModelSerializer):
    clase = ClaseListSerializer(read_only=True)
    estudiante = EstudianteListSerializer(read_only=True)

    class Meta:
        model = ClaseEstudiante
        fields = '__all__'
        depth = 1

class ClaseEstudianteCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClaseEstudiante
        fields = '__all__'

    def validate_clase(self, value: Clase):
        if value.estado == Clase.Estado.COMPLETADA:
            raise ValidationError('No es posible alterar una clase completada')
        return value

class ClaseEstudianteUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClaseEstudiante
        fields = '__all__'
        read_only_fields = ['clase', 'estudiante']

class CuotaListSerializer(serializers.ModelSerializer):
    nombre_curso = serializers.CharField(source='curso.nombre', read_only=True)
    cantidad_clases = serializers.IntegerField(read_only=True)

    class Meta:
        model = Cuota
        exclude = [
            'fecha_registro',
            'fecha_actualizacion',
            'clases'
        ]

class CuotaReadSerializer(serializers.ModelSerializer):
    clases = ClaseListSerializer(many=True, read_only=True)

    class Meta:
        model = Cuota
        fields = '__all__'
        depth = 1

class CuotaCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cuota
        fields = '__all__'

    def validate(self, attrs: dict):
        tipo = attrs.get('tipo')
        mes = attrs.get('mes')
        anio = attrs.get('anio')
        cantidad_clases = attrs.get('cantidad_clases')
        clases = attrs.get('clases')
        curso = attrs.get('curso')

        # Comprueba si se establecio el tipo de cuota
        if tipo:
            # Para mensualidad: requiere de mes y año
            if tipo == Cuota.Tipo.MENSUALIDAD and None in [mes, anio]:
                raise ValidationError({'tipo': 'Una cuota de mensualidad debe definir mes y año'})
            # Para inscripción: requiere de mes o año
            elif tipo == Cuota.Tipo.INSCRIPCION and curso is None and anio is None:
                raise ValidationError({'tipo': 'Una cuota de inscripción debe definir año o curso'})
            # Para clase individual: requiere una sola clase
            elif tipo == Cuota.Tipo.CLASE_INDIVIDUAL and clases is not None and len(clases) > 1:
                raise ValidationError({'tipo': 'Una cuota de clase no debe contener más de una'})
            # Para paquete de clases: requiere de una cantidad de clases mayor que 1
            elif tipo == Cuota.Tipo.PAQUETE_CLASES:
                if clases is not None:
                    cantidad_clases = len(clases)

                if cantidad_clases is None:
                    raise ValidationError({'tipo': 'Un paquete de clases debe definir la cantidad de clases'})
                elif cantidad_clases <= 1:
                    raise ValidationError({'tipo': 'Un paquete de clases debe tener más de una clase'})

        return attrs

class CuotaUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cuota
        fields = '__all__'
        read_only_fields = ['tipo', 'curso', 'mes', 'anio']

class PagoEstudianteCuotaSerializer(serializers.ModelSerializer):
    cuota = CuotaListSerializer(read_only=True)

    class Meta:
        model = CuotaPagada
        exclude = ['pago']
        depth = 1

class PagoEstudianteListSerializer(serializers.ModelSerializer):
    nombre_estudiante = serializers.CharField(source='estudiante.nombre_completo', read_only=True)
    cantidad_cuotas = serializers.IntegerField(read_only=True)

    class Meta:
        model = PagoEstudiante
        exclude = ['cuotas']

class PagoEstudianteReadSerializer(serializers.ModelSerializer):
    estudiante = EstudianteListSerializer(read_only=True)
    cuotas = PagoEstudianteCuotaSerializer(source='cuotas_pago', many=True, read_only=True)

    class Meta:
        model = PagoEstudiante
        fields = '__all__'
        depth = 1

class PagoEstudianteCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PagoEstudiante
        fields = '__all__'
        read_only_fields = ['total']

class PagoEstudianteUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PagoEstudiante
        fields = '__all__'
        read_only_fields = ['estudiante', 'total']

class PagoInstructorListSerializer(serializers.ModelSerializer):
    nombre_instructor = serializers.CharField(source='instructor.nombre_completo', read_only=True)
    concepto_salario = serializers.CharField(source='salario.concepto', read_only=True)

    class Meta:
        model = PagoInstructor
        fields = '__all__'

class PagoInstructorReadSerializer(serializers.ModelSerializer):
    instructor = InstructorListSerializer(read_only=True)

    class Meta:
        model = PagoInstructor
        fields = '__all__'
        depth = 1

class PagoInstructorCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PagoInstructor
        fields = '__all__'
        read_only_fields = ['monto']

class PagoInstructorUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PagoInstructor
        fields = '__all__'
        read_only_fields = ['instructor', 'salario', 'monto']

class CuotaPagadaReadSerializer(serializers.ModelSerializer):
    pago = PagoEstudianteListSerializer(read_only=True)
    cuota = CuotaListSerializer(read_only=True)

    class Meta:
        model = CuotaPagada
        fields = '__all__'
        depth = 1

class CuotaPagadaWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = CuotaPagada
        fields = '__all__'
        read_only_fields = ['monto']

    def validate_pago(self, value: PagoEstudiante):
        if value.estado.es_finalizado():
            raise ValidationError('No es posible alterar un pago finalizado')
        return value

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
                'non_field_errors': 'Debe establecer un identificador de estudiante, instructor o pago.'
                }
            )
        if counter > 1:
            raise serializers.ValidationError({
                'non_field_errors': 'No se pueden establecer más de un identificador de estudiante, instructor o pago al mismo tiempo.'
                }
            )

        return attrs

class DocumentoUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Documento
        fields = '__all__'
        read_only_fields = ['id', 'estudiante', 'instructor', 'pago', 'archivo']
