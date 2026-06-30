import joblib
import numpy as np
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import ActaElectoral
from .serializers import ActaElectoralSerializer

class ActaViewSet(viewsets.ModelViewSet):
    queryset = ActaElectoral.objects.all()
    serializer_class = ActaElectoralSerializer

    @action(detail=False, methods=['get'])
    def anomalias(self, request):
        actas_sospechosas = ActaElectoral.objects.filter(es_anomala=True).order_by('-porcentaje_riesgo')
        serializer = self.get_serializer(actas_sospechosas, many=True)
        return Response(serializer.data)

    # NUEVO ENDPOINT PARA EL SIMULADOR EN VIVO
    @action(detail=False, methods=['post'])
    def simular(self, request):
        datos = request.data
        
        # 1. Cargar la IA entrenada
        modelo = joblib.load('modelo_ia.pkl')
        scaler = joblib.load('scaler_ia.pkl')
        umbral = joblib.load('umbral_ia.pkl')

        # 2. Preparar los datos exactos como los lee la red
        X_nuevo = np.array([[
            int(datos['empadronados']), 
            int(datos['votos_validos']), 
            int(datos['votos_blancos']), 
            int(datos['votos_nulos'])
        ]])
        X_scaled = scaler.transform(X_nuevo)
        
        # 3. Predicción matemática
        X_pred = modelo.predict(X_scaled)
        error_acta = np.mean(np.power(X_scaled - X_pred, 2))
        
        es_anomala = bool(error_acta > umbral)
        riesgo = min(round((error_acta / umbral) * 100, 2), 100.0) if es_anomala else min(round((error_acta / umbral) * 50, 2), 99.0)
        
        # 4. Guardar en base de datos para que aparezca en el Dashboard
        ActaElectoral.objects.create(
            codigo_acta=datos['codigo_acta'],
            canton=datos['canton'],
            parroquia=datos['parroquia'],
            zona="Zona_Demo",
            junta="DEMO",
            empadronados=datos['empadronados'],
            votos_validos=datos['votos_validos'],
            votos_blancos=datos['votos_blancos'],
            votos_nulos=datos['votos_nulos'],
            hora_ingreso=timezone.now(),
            es_anomala=es_anomala,
            porcentaje_riesgo=riesgo
        )
        
        return Response({
            'es_anomala': es_anomala,
            'riesgo': riesgo
        })