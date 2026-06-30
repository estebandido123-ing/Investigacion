from django.db import models

class ActaElectoral(models.Model):
    # Datos de Ubicación
    codigo_acta = models.CharField(max_length=50, unique=True)
    canton = models.CharField(max_length=100)
    parroquia = models.CharField(max_length=100)
    zona = models.CharField(max_length=100)
    junta = models.CharField(max_length=10)
    
    # Datos Numéricos (Variables Independientes para la IA)
    empadronados = models.IntegerField()
    votos_validos = models.IntegerField()
    votos_blancos = models.IntegerField()
    votos_nulos = models.IntegerField()
    
    # Datos de Control
    hora_ingreso = models.DateTimeField()
    
    # Resultados del Análisis (Variables Dependientes)
    es_anomala = models.BooleanField(default=False, null=True)
    porcentaje_riesgo = models.FloatField(default=0.0, null=True)

    def __str__(self):
        return f"Acta {self.codigo_acta} - {self.parroquia}"