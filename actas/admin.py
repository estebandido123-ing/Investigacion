from django.contrib import admin
from .models import ActaElectoral

@admin.register(ActaElectoral)
class ActaElectoralAdmin(admin.ModelAdmin):
    # Esto define qué columnas veremos en la tabla del panel web
    list_display = ('codigo_acta', 'canton', 'parroquia', 'es_anomala', 'porcentaje_riesgo')
    list_filter = ('es_anomala', 'canton')
    search_fields = ('codigo_acta', 'parroquia')