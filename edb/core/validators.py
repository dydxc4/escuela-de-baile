from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible
from django.core.validators import RegexValidator, MinValueValidator
from django.utils import timezone
from edb.settings import MAX_UPLOAD_FILE_SIZE_BYTES, MAX_UPLOAD_FILE_SIZE_MB

# Validador de números de teléfono
phone_number_validator = RegexValidator(
    regex=r'^(\+?\d{1,3}-)?\d{3}-\d{3}-\d{4}$',
    message='Ingrese un número de teléfono en formato 000-000-000 o +00-000-000-000'
)

price_validator = MinValueValidator(
    limit_value=0,
    message='Ingrese un monto igual o mayor que cero'
)

def validate_month(value: int):
    if value < 1 or value > 12:
        raise ValidationError("Ingrese un número de mes válido")

def validate_year(value: int):
    if value < 2026 or value > 2100:
        raise ValidationError("Ingrese un año válido")

def validate_file_size(file):
    if file.size > MAX_UPLOAD_FILE_SIZE_BYTES:
        raise ValidationError(f'El archivo es demasiado grande. El máximo permitido son {MAX_UPLOAD_FILE_SIZE_MB} MB.')
