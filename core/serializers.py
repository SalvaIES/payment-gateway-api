from rest_framework import serializers
from .models import Provider, Transaction


class ProviderSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Provider."""

    class Meta:
        model = Provider
        fields = '__all__'
        read_only_fields = ['created_at']


class TransactionSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Transaction."""

    provider_name = serializers.CharField(
        source='provider.name',
        read_only=True
    )

    class Meta:
        model = Transaction
        fields = '__all__'
        read_only_fields = [
            'created_at',
            'updated_at',
            'stripe_client_secret'
        ]

    def validate_amount(self, value):
        """El importe debe ser mayor que cero."""
        if value <= 0:
            raise serializers.ValidationError(
                "El importe debe ser mayor que cero."
            )
        return value

    def validate(self, data):
        """Si el estado es failed, el tipo de incidencia es obligatorio."""
        if data.get('status') == 'failed' and not data.get('incident_type'):
            raise serializers.ValidationError(
                "Debe especificar un tipo de incidencia "
                "cuando el estado es 'failed'."
            )
        return data
