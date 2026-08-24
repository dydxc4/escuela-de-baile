from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(TipoDocumento)
admin.site.register(Salario)
admin.site.register(Estudiante)
admin.site.register(Tutor)
admin.site.register(Instructor)
admin.site.register(TutorEstudiante)
admin.site.register(Curso)
admin.site.register(Periodo)
admin.site.register(Clase)
admin.site.register(ClaseEstudiante)
admin.site.register(Cuota)
admin.site.register(PagoEstudiante)
admin.site.register(PagoInstructor)
