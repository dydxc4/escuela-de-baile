from django.db import models
from django.core.validators import FileExtensionValidator
from django_enum import EnumField
from .validators import *
from .utils import generate_uuid_filename
from edb.settings import UPLOAD_ALLOWED_EXTENSIONS

# Create your models here.

class TipoDocumento(models.Model):
    nombre = models.CharField(max_length=60)

    def __str__(self) -> str:
        return self.nombre

class Salario(models.Model):
    concepto = models.CharField(max_length=120, unique=True)
    monto = models.DecimalField(max_digits=8, decimal_places=2, validators=[price_validator])
    fecha_registro = models.DateTimeField(auto_now_add=True)
    esta_habilitado = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f'{self.concepto}: ${self.monto}'

class Persona(models.Model):
    nombre = models.CharField(max_length=80)
    apellido_paterno = models.CharField(max_length=40)
    apellido_materno = models.CharField(max_length=40, null=True, blank=True)
    correo_electronico = models.EmailField(null=True, blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True

    def __str__(self) -> str:
        nombre_completo = f'{self.nombre} {self.apellido_paterno}'

        if self.apellido_materno is not None:
            nombre_completo += f' {self.apellido_materno}'

        return nombre_completo.strip()

class Estudiante(Persona):
    class Genero(models.TextChoices):
        HOMBRE = 'HOMBRE', 'Hombre'
        MUJER = 'MUJER', 'Mujer'
        NO_BINARIO = 'NO_BINARIO', 'No binario'

    class Estado(models.TextChoices):
        ACTIVO = 'ACTIVO', 'Activo'
        PAGO_PENDIENTE = 'PAGO_PENDIENTE', 'Pago pendiente'
        BAJA = 'BAJA', 'Baja'

    telefono = models.CharField(max_length=20, null=True, blank=True, validators=[phone_number_validator])
    curp = models.CharField(max_length=18, unique=True)
    fecha_nacimiento = models.DateField()
    genero = EnumField(Genero, null=True, blank=True)
    estado_inscripcion = EnumField(Estado, default=Estado.ACTIVO)
    posee_tarjeta_asistencia = models.BooleanField()

class Tutor(Persona):
    telefono = models.CharField(max_length=20, validators=[phone_number_validator])
    estudiantes = models.ManyToManyField(Estudiante, related_name='tutores', through='TutorEstudiante')

class Instructor(Persona):
    salario = models.ForeignKey(Salario, related_name='instructores', on_delete=models.RESTRICT)
    telefono = models.CharField(max_length=20, unique=True, validators=[phone_number_validator])
    correo_electronico = models.EmailField(unique=True)
    esta_habilitado = models.BooleanField(default=True)

class TutorEstudiante(models.Model):
    class Parentesco(models.TextChoices):
        PADRE = 'PADRE', 'Padre'
        MADRE = 'MADRE', 'Madre'
        HERMANO = 'HERMANO', 'Hermano/a'
        TIO = 'TIO', 'Tío/a'
        ABUELO = 'ABUELO', 'Abuelo/a'
        TUTOR_LEGAL = 'TUTOR_LEGAL', 'Tutor legal'

    tutor = models.ForeignKey(Tutor, related_name='estudiantes_tutor', on_delete=models.RESTRICT)
    estudiante = models.ForeignKey(Estudiante, related_name='tutores_estudiante', on_delete=models.RESTRICT)
    parentesco = EnumField(Parentesco)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['tutor', 'estudiante'], name='unique_tutor_estudiante'
            )
        ]

    def __str__(self) -> str:
        return f'{self.tutor} {self.parentesco.label.lower()} de {self.estudiante}'

class Curso(models.Model):
    nombre = models.CharField(max_length=80)
    descripcion = models.TextField(max_length=640, null=True, blank=True)
    esta_habilitado = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.nombre

class Periodo(models.Model):
    curso = models.ForeignKey(Curso, related_name='periodos', on_delete=models.RESTRICT)
    fecha_inicio = models.DateField()
    fecha_finalizacion = models.DateField()

    def __str__(self) -> str:
        return f'{self.curso} ({self.fecha_inicio} - {self.fecha_finalizacion})'

class Clase(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = 'PENDIENTE', 'Pendiente'
        EN_CURSO = 'EN_CURSO', 'En curso'
        APLAZADA = 'APLAZADA', 'Aplazada'
        COMPLETADA = 'COMPLETADA', 'Completada'

    periodo = models.ForeignKey(Periodo, related_name='clases', on_delete=models.RESTRICT)
    instructor = models.ForeignKey(Instructor, related_name='clases', on_delete=models.RESTRICT)
    fecha_hora = models.DateTimeField()
    duracion = models.DurationField()
    descripcion = models.CharField(max_length=120, null=True, blank=True)
    estado = EnumField(Estado, default=Estado.PENDIENTE)
    estudiantes = models.ManyToManyField(Estudiante, related_name='clases', null=True, blank=True)

    def __str__(self) -> str:
        return f'{self.periodo} - Clase {self.fecha_hora} [{self.estado}]'

class Cuota(models.Model):
    class Tipo(models.TextChoices):
        INSCRIPCION = 'INSCRIPCION', 'Inscripción'
        MENSUALIDAD = 'MENSUALIDAD', 'Mensualidad'
        CLASE_INDIVIDUAL = 'CLASE_INDIVIDUAL', 'Clase individual'
        PAQUETE_CLASES = 'PAQUETE_CLASES', 'Paquete de clases'

    periodo = models.ForeignKey(Periodo, related_name='cuotas', on_delete=models.CASCADE)
    tipo = EnumField(Tipo)
    concepto = models.CharField(max_length=120, unique=True)
    costo = models.DecimalField(max_digits=8, decimal_places=2, validators=[price_validator])
    fecha_limite = models.DateTimeField(null=True, blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    esta_habilitado = models.BooleanField(default=True)
    clases = models.ManyToManyField(Clase, related_name='cuotas', null=True, blank=True)

    def __str__(self) -> str:
        return f'{self.concepto}: ${self.costo}'

class PagoEstudiante(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = 'PENDIENTE', 'Pendiente'
        POR_CONFIRMAR = 'POR_CONFIRMAR', 'Por confirmar'
        COMPLETADO = 'COMPLETADO', 'Completado'
        CANCELADO = 'CANCELADO', 'Cancelado'
        DEVUELTO = 'DEVUELTO', 'Devuelto'

    estudiante = models.ForeignKey(Estudiante, related_name='pagos', on_delete=models.RESTRICT)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_confirmacion = models.DateTimeField(null=True, blank=True)
    total = models.DecimalField(max_digits=8, decimal_places=2)
    estado = EnumField(Estado, default=Estado.PENDIENTE)
    cuotas = models.ManyToManyField(Cuota, related_name='pagos_estudiantes')

    def __str__(self) -> str:
        return f'{self.estudiante} - {self.fecha_registro}: ${self.total}'

class PagoInstructor(models.Model):
    instructor = models.ForeignKey(Instructor, related_name='pagos', on_delete=models.RESTRICT)
    salario = models.ForeignKey(Salario, related_name='instructores_salario', on_delete=models.RESTRICT)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    monto = models.DecimalField(max_digits=8, decimal_places=2)
    esta_confirmado = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f'{self.instructor} - {self.fecha_registro}: ${self.monto}'

class Documento(models.Model):
    estudiante = models.ForeignKey(Estudiante, related_name='documentos', on_delete=models.CASCADE, null=True, blank=True)
    instructor = models.ForeignKey(Instructor, related_name='documentos', on_delete=models.CASCADE, null=True, blank=True)
    pago = models.ForeignKey(PagoEstudiante, related_name='documentos', on_delete=models.CASCADE, null=True, blank=True)
    tipo = models.ForeignKey(TipoDocumento, related_name='documentos', on_delete=models.RESTRICT, null=True, blank=True)
    archivo = models.FileField(
        upload_to=generate_uuid_filename,
        validators=[
            FileExtensionValidator(allowed_extensions=UPLOAD_ALLOWED_EXTENSIONS),
            validate_file_size
        ]
    )
    notas = models.TextField(max_length=120, null=True, blank=True)
    fecha_subida = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f'Documento #{self.pk}: {self.archivo.name} ({self.fecha_subida})'
