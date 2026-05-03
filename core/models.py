from django.db import models


class Provider(models.Model):
    """Representa una pasarela de pago (Stripe, PayPal, Redsys)."""

    ENVIRONMENT_CHOICES = [
        ('sandbox', 'Sandbox'),
        ('production', 'Production'),
    ]

    name = models.CharField(max_length=100)
    api_key = models.CharField(max_length=255)
    environment = models.CharField(
        max_length=20,
        choices=ENVIRONMENT_CHOICES,
        default='sandbox'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Devuelve la representación en texto del proveedor."""
        return f"{self.name} ({self.environment})"

    class Meta:
        ordering = ['name']


class Transaction(models.Model):
    """Registra cada intento de pago asociado a un proveedor."""

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    INCIDENT_CHOICES = [
        ('', 'Sin incidencia'),
        ('impago', 'Impago'),
        ('error_conexion', 'Error de conexión'),
        ('devolucion', 'Devolución'),
    ]

    provider = models.ForeignKey(
        Provider,
        on_delete=models.PROTECT,
        related_name='transactions'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='EUR')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    incident_type = models.CharField(
        max_length=20,
        choices=INCIDENT_CHOICES,
        blank=True,
        default=''
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """Devuelve la representación en texto de la transacción."""
        return (
            f"{self.provider.name} — {self.amount} "
            f"{self.currency} ({self.status})"
        )

    class Meta:
        ordering = ['-created_at']
