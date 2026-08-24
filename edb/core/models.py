from django.db import models
from django.core.validators import MinValueValidator
from django_enum import EnumField
from .validators import phone_number_validator, price_validator

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
        return f'{self.nombre} {self.apellido_paterno} {self.apellido_materno}'.strip()

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
    fecha_nacimiento = models.DateTimeField()
    genero = EnumField(Genero, null=True)
    estado_inscripcion = EnumField(Estado, default=Estado.ACTIVO)
    posee_tarjeta_asistencia = models.BooleanField()

class Tutor(Persona):
    telefono = models.CharField(max_length=20, validators=[phone_number_validator])
    estudiantes = models.ManyToManyField(Estudiante, through='TutorEstudiante')

class Instructor(Persona):
    salario = models.ForeignKey(Salario, on_delete=models.RESTRICT)
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

    tutor = models.ForeignKey(Tutor, on_delete=models.RESTRICT)
    estudiante = models.ForeignKey(Estudiante, on_delete=models.RESTRICT)
    parentesco = EnumField(Parentesco)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['tutor', 'estudiante'], name='unique_tutor_estudiante'
            )
        ]

    def __str__(self) -> str:
        return f'{self.estudiante} {self.parentesco} de {self.tutor}'

class Curso(models.Model):
    nombre = models.CharField(max_length=80)
    descripcion = models.TextField(max_length=640, null=True, blank=True)
    esta_habilitado = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.nombre

class Periodo(models.Model):
    curso = models.ForeignKey(Curso, on_delete=models.RESTRICT)
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

    periodo = models.ForeignKey(Periodo, on_delete=models.RESTRICT)
    instructor = models.ForeignKey(Instructor, on_delete=models.RESTRICT)
    fecha_hora = models.DateTimeField()
    duracion = models.DurationField()
    estado = EnumField(Estado, default=Estado.PENDIENTE)
    estudiantes = models.ManyToManyField(Estudiante, through='ClaseEstudiante')

    def __str__(self) -> str:
        return f'{self.periodo} - Clase {self.fecha_hora} [{self.estado}]'

class ClaseEstudiante(models.Model):
    clase = models.ForeignKey(Clase, on_delete=models.CASCADE)
    estudiante = models.ForeignKey(Estudiante, on_delete=models.RESTRICT)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['clase', 'estudiante'], name='unique_clase_estudiante'
            )
        ]

    def __str__(self) -> str:
        return f'{self.estudiante} - {self.clase}'

class Cuota(models.Model):
    class Tipo(models.TextChoices):
        INSCRIPCION = 'INSCRIPCION', 'Inscripción'
        MENSUALIDAD = 'MENSUALIDAD', 'Mensualidad'
        CLASE_INDIVIDUAL = 'CLASE_INDIVIDUAL', 'Clase individual'
        PAQUETE_CLASES = 'PAQUETE_CLASES', 'Paquete de clases'

    periodo = models.ForeignKey(Periodo, on_delete=models.CASCADE)
    tipo = EnumField(Tipo)
    concepto = models.CharField(max_length=120, unique=True)
    costo = models.DecimalField(max_digits=8, decimal_places=2, validators=[price_validator])
    fecha_limite = models.DateTimeField(null=True, blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    esta_habilitado = models.BooleanField(default=True)
    clases = models.ManyToManyField(Clase)

    def __str__(self) -> str:
        return f'{self.concepto}: ${self.costo}'

class PagoEstudiante(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = 'PENDIENTE', 'Pendiente'
        POR_CONFIRMAR = 'POR_CONFIRMAR', 'Por confirmar'
        COMPLETADO = 'COMPLETADO', 'Completado'
        CANCELADO = 'CANCELADO', 'Cancelado'
        DEVUELTO = 'DEVUELTO', 'Devuelto'

    estudiante = models.ForeignKey(Estudiante, on_delete=models.RESTRICT)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_confirmacion = models.DateTimeField(null=True, blank=True)
    total = models.DecimalField(max_digits=8, decimal_places=2)
    estado = EnumField(Estado, default=Estado.PENDIENTE)
    cuotas = models.ManyToManyField(Cuota)

    def __str__(self) -> str:
        return f'{self.estudiante} - {self.fecha_registro}: ${self.total}'

class PagoInstructor(models.Model):
    instructor = models.ForeignKey(Instructor, on_delete=models.RESTRICT)
    salario = models.ForeignKey(Salario, on_delete=models.RESTRICT)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    monto = models.DecimalField(max_digits=8, decimal_places=2)
    esta_confirmado = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f'{self.instructor} - {self.fecha_registro}: ${self.monto}'
