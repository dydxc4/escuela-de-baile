from django.db.models import Q
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

class MensualidadSerializer(serializers.ModelSerializer):
    fecha_pago = serializers.SerializerMethodField(read_only=True)
    monto_pago = serializers.DecimalField(source='pago.monto', max_digits=8, decimal_places=2)

    class Meta:
        model = MensualidadPagada
        exclude = ['estudiante']

    def get_fecha_pago(self, obj: MensualidadPagada):
        return (obj.pago.fecha_confirmacion or obj.pago.fecha_registro).date()

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

class TutorEstudianteSerializer(serializers.ModelSerializer):
    tutor = TutorListSerializer(read_only=True)

    class Meta:
        model = TutorEstudiante
        exclude = ['estudiante']
        depth = 1

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
    cantidad_asistencias = serializers.IntegerField(read_only=True)

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

    def validate_estudiante(self, value):
        if value.estado_inscripcion != Estudiante.Estado.ACTIVO:
            raise ValidationError('No es posible agregar a un estudiante que ha sido dado de baja o tiene pagos pendientes')

        if not value.esta_al_corriente:
            if value.contador_clases_restantes == 0:
                raise ValidationError('No es posible agregar a un estudiante que está atrasado con el pago de la mensualidad o ya no tiene clases restantes')

            clases_pendientes = value.clases_estudiante \
                .filter(~Q(clase__estado=Clase.Estado.COMPLETADA) & Q(asistio=False)) \
                .count()

            if value.contador_clases_restantes <= clases_pendientes:
                raise ValidationError('El estudiante ya no posee más clases restantes para inscribirse')

        return value

class ClaseEstudianteUpdateSerializer(ClaseEstudianteCreateSerializer   ):
    class Meta(ClaseEstudianteCreateSerializer.Meta):
        read_only_fields = ['clase', 'estudiante']

class ClaseEstudianteSerializer(serializers.ModelSerializer):
    clase = ClaseListSerializer(read_only=True)

    class Meta:
        model = ClaseEstudiante
        exclude = ['estudiante']
        depth = 1

class EstudianteSerializer(serializers.ModelSerializer):
    edad = serializers.IntegerField(read_only=True)
    rango_edad = serializers.CharField(read_only=True)
    mensualidades = MensualidadSerializer(many=True, read_only=True)
    esta_al_corriente = serializers.BooleanField(read_only=True)
    tutores = TutorEstudianteSerializer(source='tutores_estudiante', many=True, read_only=True)
    clases = ClaseEstudianteSerializer(source='clases_estudiante', many=True, read_only=True)

    class Meta:
        model = Estudiante
        fields = '__all__'
        read_only_fields = ['contador_clases_restantes']

class CuotaListSerializer(serializers.ModelSerializer):
    nombre_curso = serializers.CharField(source='curso.nombre', read_only=True)
    cantidad_clases = serializers.IntegerField(read_only=True)

    class Meta:
        model = Cuota
        exclude = [
            'fecha_registro',
            'fecha_actualizacion',
        ]

class CuotaReadSerializer(serializers.ModelSerializer):
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
        cantidad_clases = attrs.get('cantidad_clases')

        # Comprueba si se establecio el tipo de cuota
        if tipo:
            # Para clase individual: requiere una sola clase
            if tipo == Cuota.Tipo.CLASE_INDIVIDUAL and cantidad_clases is not None and cantidad_clases > 1:
                raise ValidationError({'tipo': 'Una cuota de clase no debe contener más de una'})
            # Para paquete de clases: requiere de una cantidad de clases mayor que 1
            elif tipo == Cuota.Tipo.PAQUETE_CLASES:
                if cantidad_clases is None:
                    raise ValidationError({'tipo': 'Un paquete de clases debe definir la cantidad de clases'})
                elif cantidad_clases <= 1:
                    raise ValidationError({'tipo': 'Un paquete de clases debe tener más de una clase'})

        return attrs

class CuotaUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cuota
        fields = '__all__'
        read_only_fields = ['tipo', 'curso']

class PagoEstudianteListSerializer(serializers.ModelSerializer):
    nombre_estudiante = serializers.CharField(source='estudiante.nombre_completo', read_only=True)
    tipo_cuota = serializers.CharField(source='cuota.tipo', read_only=True)
    concepto_cuota = serializers.CharField(source='cuota.concepto', read_only=True)

    class Meta:
        model = PagoEstudiante
        fields = '__all__'

class PagoEstudianteReadSerializer(serializers.ModelSerializer):
    estudiante = EstudianteListSerializer(read_only=True)
    cuota = CuotaListSerializer(read_only=True)

    class Meta:
        model = PagoEstudiante
        fields = '__all__'
        depth = 1

class PagoEstudianteCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PagoEstudiante
        fields = '__all__'
        read_only_fields = ['monto']

    def validate_cuota(self, value: Cuota):
        if not value.esta_habilitado:
            raise ValidationError('No es posible realizar el pago de una cuota deshabilitada')
        return value

    def validate(self, attrs: dict):
        cuota = attrs.get('cuota', self.instance.cuota if self.instance else None)
        estudiante = attrs.get('estudiante', self.instance.estudiante if self.instance else None)

        # Validación de pago de mensualidad
        if cuota and estudiante and cuota.tipo == Cuota.Tipo.MENSUALIDAD:
            # Verifica si el rango de edad del estudiante corresponde a un adulto
            if estudiante.rango_edad == Estudiante.RangoEdad.ADULTO:
                raise ValidationError({'estudiante': 'Un estudiante adulto no puede pagar por mensualidad'})

            # Verifica si ya se asocio el pago actual con una mensualidad
            cantidad = MensualidadPagada.objects \
                .filter(estudiante=estudiante, pago=self.instance) \
                .count()

            if cantidad > 0:
                raise ValidationError({'cuota': 'No es posible agregar una cuota previamente pagada'})

        return attrs

class PagoEstudianteUpdateSerializer(PagoEstudianteCreateSerializer):
    class Meta(PagoEstudianteCreateSerializer.Meta):
        read_only_fields = ['cuota', 'estudiante', 'monto']

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
