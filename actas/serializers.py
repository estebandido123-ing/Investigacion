from rest_framework import serializers
from .models import ActaElectoral

class ActaElectoralSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActaElectoral
        fields = '__all__' # Esto le dice que exporte todas las columnas