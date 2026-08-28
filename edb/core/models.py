from typing import Iterable
from datetime import timedelta
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

class Curso(models.Model):
    nombre = models.CharField(max_length=80)
    descripcion = models.TextField(max_length=640, null=True, blank=True)
    esta_habilitado = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.nombre

class Persona(models.Model):
    nombre = models.CharField(max_length=80)
    apellido_paterno = models.CharField(max_length=40)
    apellido_materno = models.CharField(max_length=40, null=True, blank=True)
    correo_electronico = models.EmailField(null=True, blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True

    @property
    def nombre_completo(self):
        result = f'{self.nombre} {self.apellido_paterno}'
        if self.apellido_materno is not None:
            result += f' {self.apellido_materno}'
        return result.strip()

    def __str__(self) -> str:
        return self.nombre_completo

class Estudiante(Persona):
    class Genero(models.TextChoices):
        HOMBRE = 'HOMBRE', 'Hombre'
        MUJER = 'MUJER', 'Mujer'
        NO_BINARIO = 'NO_BINARIO', 'No binario'

    class Estado(models.TextChoices):
        ACTIVO = 'ACTIVO', 'Activo'
        PAGO_PENDIENTE = 'PAGO_PENDIENTE', 'Pago pendiente'
        BAJA = 'BAJA', 'Baja'

    class RangoEdad(models.TextChoices):
        NINIO = 'NINIO', 'Niño'
        ADOLESCENTE = 'ADOLESCENTE', 'Adolescente'
        ADULTO = 'ADULTO', 'Adulto'

    telefono = models.CharField(max_length=20, null=True, blank=True, validators=[phone_number_validator])
    curp = models.CharField(max_length=18, unique=True)
    fecha_nacimiento = models.DateField()
    genero = EnumField(Genero, null=True, blank=True)
    estado_inscripcion = EnumField(Estado, default=Estado.ACTIVO)
    posee_tarjeta_asistencia = models.BooleanField()
    contador_clases_restantes = models.PositiveIntegerField(default=0)

    @property
    def edad(self):
        today = timezone.now().date()
        age = today.year - self.fecha_nacimiento.year - \
            ((today.month, today.day) < (
                self.fecha_nacimiento.month,
                self.fecha_nacimiento.day
            ))
        return age

    @property
    def rango_edad(self) -> RangoEdad:
        # Obtiene los rangos de edades directamente de la base de datos
        config = Configuracion.load()

        if self.edad <= config.edad_max_ninio:
            return self.RangoEdad.NINIO
        elif self.edad < config.edad_min_adulto:
            return self.RangoEdad.ADOLESCENTE
        return self.RangoEdad.ADULTO

    @property
    def esta_al_corriente(self) -> bool:
        hoy = timezone.now().date()
        vigencia = self.mensualidades \
            .aggregate(vigencia=models.Max('fecha_vigencia'))['vigencia']
        return vigencia is not None and vigencia >= hoy

    @property
    def mensualidad_proxima_a_vencer(self) -> bool:
        config = Configuracion.load()
        hoy = timezone.now().date()
        margen = hoy + timedelta(days=config.margen_antes_fin_vigencia)
        result = self.mensualidades \
            .filter(fecha_vigencia__range=(hoy, margen)) \
            .exists()
        return result

    def save(self, *args, **kwargs):
        self.curp = self.curp.upper()
        super().save(*args, **kwargs)

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

class Clase(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = 'PENDIENTE', 'Pendiente'
        EN_CURSO = 'EN_CURSO', 'En curso'
        APLAZADA = 'APLAZADA', 'Aplazada'
        COMPLETADA = 'COMPLETADA', 'Completada'

    curso = models.ForeignKey(Curso, related_name='clases', on_delete=models.RESTRICT)
    instructor = models.ForeignKey(Instructor, related_name='clases', on_delete=models.RESTRICT)
    fecha_hora = models.DateTimeField()
    duracion = models.DurationField()
    descripcion = models.CharField(max_length=120, null=True, blank=True)
    estado = EnumField(Estado, default=Estado.PENDIENTE)
    estudiantes = models.ManyToManyField(Estudiante, through='ClaseEstudiante', related_name='clases')

    @property
    def cantidad_estudiantes(self):
        resultado = self.estudiantes \
            .aggregate(cantidad=models.Count('id'))['cantidad']
        return resultado or 0

    @property
    def cantidad_asistencias(self):
        resultado = self.estudiantes_clase \
            .filter(asistio=True) \
            .aggregate(cantidad=models.Count('id'))['cantidad']
        return resultado or 0

    def __str__(self) -> str:
        return f'{self.curso.nombre} - Clase {self.fecha_hora} [{self.estado}]'

class ClaseEstudiante(models.Model):
    clase = models.ForeignKey(Clase, related_name='estudiantes_clase', on_delete=models.CASCADE)
    estudiante = models.ForeignKey(Estudiante, related_name='clases_estudiante', on_delete=models.RESTRICT)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    asistio = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['clase', 'estudiante'], name='unique_clase_estudiante'
            )
        ]

    def __str__(self) -> str:
        return f'{self.estudiante} en {self.clase}'

class Cuota(models.Model):
    class Tipo(models.TextChoices):
        INSCRIPCION = 'INSCRIPCION', 'Inscripción'
        MENSUALIDAD = 'MENSUALIDAD', 'Mensualidad'
        CLASE_INDIVIDUAL = 'CLASE_INDIVIDUAL', 'Clase individual'
        PAQUETE_CLASES = 'PAQUETE_CLASES', 'Paquete de clases'

    curso = models.ForeignKey(Curso, related_name='cuotas', on_delete=models.CASCADE, null=True, blank=True)
    tipo = EnumField(Tipo)
    concepto = models.CharField(max_length=120, unique=True)
    costo = models.DecimalField(max_digits=8, decimal_places=2, validators=[price_validator])
    cantidad_clases = models.PositiveIntegerField(null=True, blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    esta_habilitado = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if self.tipo == self.Tipo.CLASE_INDIVIDUAL:
            self.cantidad_clases = 1
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f'{self.concepto}: ${self.costo}'

class PagoEstudiante(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = 'PENDIENTE', 'Pendiente'
        POR_CONFIRMAR = 'POR_CONFIRMAR', 'Por confirmar'
        COMPLETADO = 'COMPLETADO', 'Completado'
        CANCELADO = 'CANCELADO', 'Cancelado'
        DEVUELTO = 'DEVUELTO', 'Devuelto'

        def es_finalizado(self):
            return self in [self.CANCELADO, self.DEVUELTO, self.COMPLETADO]

    estudiante = models.ForeignKey(Estudiante, related_name='pagos', on_delete=models.RESTRICT)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_confirmacion = models.DateTimeField(null=True, blank=True)
    monto = models.DecimalField(max_digits=8, decimal_places=2)
    estado = EnumField(Estado, default=Estado.PENDIENTE)
    cuota = models.ForeignKey(Cuota, related_name='pagos', on_delete=models.RESTRICT)

    def clean(self):
        if self.pk:
            original = PagoEstudiante.objects.get(pk=self.pk)
            if original.estado.es_finalizado():
                raise ValidationError('No es posible modificar una transacción finalizada')

        super().clean()

    def save(self, *args, **kwargs):
        if self.estado == PagoEstudiante.Estado.COMPLETADO and not self.fecha_confirmacion:
            self.fecha_confirmacion = timezone.now()
        if not self.monto:
            self.monto = self.cuota.costo
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f'{self.estudiante} - {self.cuota.concepto} ({self.fecha_registro.date()})'

class PagoInstructor(models.Model):
    instructor = models.ForeignKey(Instructor, related_name='pagos', on_delete=models.RESTRICT)
    salario = models.ForeignKey(Salario, related_name='instructores_salario', on_delete=models.RESTRICT)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    monto = models.DecimalField(max_digits=8, decimal_places=2)
    esta_confirmado = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.monto:
            self.monto = self.salario.monto
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f'{self.instructor} - {self.salario.concepto} ({self.fecha_registro.date()})'

class MensualidadPagada(models.Model):
    estudiante = models.ForeignKey(Estudiante, related_name='mensualidades', on_delete=models.RESTRICT)
    pago = models.ForeignKey(PagoEstudiante, related_name='pago_estudiantes', on_delete=models.RESTRICT)
    fecha_vigencia = models.DateField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['estudiante', 'pago'], name='unique_estudiante_pago'
            )
        ]

    @property
    def esta_vigente(self):
        return timezone.now().date() <= self.fecha_vigencia

    def __str__(self) -> str:
        return f'{self.estudiante}: pagada {self.pago.fecha_registro.date()}, vigencia {self.fecha_vigencia}'

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

class AlertaEstudiante(models.Model):
    class Tipo(models.TextChoices):
        MENSUALIDAD_VENCIDA = 'MENSUALIDAD_VENCIDA', 'Mensualidad vencida'
        MENSUALIDAD_PROXIMA = 'MENSUALIDAD_PROXIMA', 'Mensualidad próxima a vencer'
        CLASES_AGOTADAS = 'CLASES_AGOTADAS', 'Sin clases restantes'

    estudiante = models.ForeignKey(Estudiante, related_name='alertas', on_delete=models.CASCADE)
    tipo = EnumField(Tipo)
    fecha = models.DateTimeField(auto_now_add=True)
    descripcion = models.TextField(max_length=120, null=True, blank=True)

    def __str__(self) -> str:
        return f'{self.estudiante} ({self.fecha.date()}): {self.tipo}'

# Modelos independientes

class Configuracion(models.Model):
    edad_max_ninio = models.PositiveSmallIntegerField(default=12)
    edad_min_adulto = models.PositiveSmallIntegerField(default=18)
    margen_antes_fin_vigencia = models.PositiveSmallIntegerField(default=10)
    intervalo_comprobacion = models.PositiveIntegerField(default=24)
    alertar_fin_mensualidad = models.BooleanField(default=True)
    alertar_clases_agotadas = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

class RegistroDiario(models.Model):
    fecha = models.DateField(auto_now_add=True, unique=True)
    ingreso_total = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    egreso_total = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    ganancia_total = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    perdida_total = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    ticket_promedio = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    cantidad_transacciones = models.PositiveIntegerField(default=0)
    cantidad_ventas = models.PositiveIntegerField(default=0)
    cantidad_cancelaciones = models.PositiveIntegerField(default=0)
    cantidad_devoluciones = models.PositiveIntegerField(default=0)
    cantidad_salarios = models.PositiveIntegerField(default=0)

    @classmethod
    def load(cls):
        hoy = timezone.now().date()
        obj, created = cls.objects.get_or_create(fecha=hoy)
        return obj

    def save(self, *args, **kwargs):
        self.ganancia_total = self.ingreso_total - self.egreso_total
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f'{self.fecha}: ingresos ${self.ingreso_total}, egresos: ${self.egreso_total}'
