from django.db.models import Sum, Q
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import CuotaPagada, PagoEstudiante, Cuota

@receiver(post_save, sender=CuotaPagada)
@receiver(post_delete, sender=CuotaPagada)
def update_total_pago_trigger(sender, instance: CuotaPagada, **kwargs):
    payment = instance.pago
    new_total = payment.cuotas.aggregate(total=Sum('costo')).get('total') or 0
    payment.total = new_total
    payment.save(update_fields=['total'])
