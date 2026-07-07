import os
import pickle
import numpy as np
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import ActaElectoral
from .serializers import ActaElectoralSerializer
from django.core.management import call_command

class ActaViewSet(viewsets.ModelViewSet):
    queryset = ActaElectoral.objects.all()
    serializer_class = ActaElectoralSerializer

    @action(detail=False, methods=['get'])
    def anomalias(self, request):
        anio_solicitado = request.query_params.get('anio', 2026) 
        canton_ref = request.query_params.get('canton_ref', 'TODOS')
        
        todas_actas = ActaElectoral.objects.filter(anio_eleccion=anio_solicitado)
        
        # 1. Alertas de Fraude
        actas_sospechosas = todas_actas.filter(es_anomala=True).order_by('-porcentaje_riesgo')
        
        # 2. Extraer lista de cantones únicos (para el menú de React)
        cantones_disponibles = list(todas_actas.exclude(canton='').values_list('canton', flat=True).distinct().order_by('canton'))
        
        # 3. Referencias Normales (Filtradas por el cantón seleccionado)
        actas_normales = todas_actas.filter(es_anomala=False)
        if canton_ref != 'TODOS':
            actas_normales = actas_normales.filter(canton=canton_ref)
            
        actas_normales = actas_normales.order_by('?')[:5] # Tomamos 5 al azar del cantón elegido
        
        data_anomalias = self.get_serializer(actas_sospechosas, many=True).data
        data_normales = self.get_serializer(actas_normales, many=True).data
        
        return Response({
            'total_registros': todas_actas.count(),
            'total_alertas': actas_sospechosas.count(),
            'anomalias': data_anomalias,
            'referencia': data_normales,
            'cantones_disponibles': cantones_disponibles # Enviamos la lista al frontend
        })
    # --- NUEVO ENDPOINT: PANEL DE CONTROL IA ---
    @action(detail=False, methods=['post'])
    def reentrenar(self, request):
        try:
            # Esto ejecuta tu comando 'python manage.py ejecutar_auditoria' desde el botón web
            call_command('ejecutar_auditoria')
            return Response({'status': 'success', 'message': 'Red Neuronal reentrenada y base de datos auditada exitosamente.'})
        except Exception as e:
            return Response({'status': 'error', 'message': str(e)}, status=500)

    @action(detail=False, methods=['post'])
    def simular(self, request):
        datos = request.data
        
        ruta_modelo = os.path.join('actas', 'models', 'modelo_auditoria.pkl')
        with open(ruta_modelo, 'rb') as f:
            datos_ia = pickle.load(f)
            modelo = datos_ia['modelo']
            scaler = datos_ia['scaler']
            
        umbral = 0.5 

        X_nuevo = np.array([[
            int(datos['empadronados']), 
            int(datos['votos_validos']), 
            int(datos['votos_blancos']), 
            int(datos['votos_nulos'])
        ]])
        X_scaled = scaler.transform(X_nuevo)
        
        X_pred = modelo.predict(X_scaled)
        error_acta = np.mean(np.power(X_scaled - X_pred, 2))
        
        es_anomala = bool(error_acta > umbral)
        
        if es_anomala:
            riesgo = min(round((error_acta / umbral) * 100, 2), 100.0)
        else:
            riesgo = min(round((error_acta / umbral) * 50, 2), 15.0) 
        
        ActaElectoral.objects.create(
            anio_eleccion=2026,
            codigo_acta=datos.get('codigo_acta', 'SIMULACION-EN-VIVO'),
            canton=datos['canton'],
            parroquia=datos.get('parroquia', 'Demo Parroquia'),
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

    @action(detail=False, methods=['post'])
    def simular(self, request):
        datos = request.data
        
        ruta_modelo = os.path.join('actas', 'models', 'modelo_auditoria.pkl')
        with open(ruta_modelo, 'rb') as f:
            datos_ia = pickle.load(f)
            modelo = datos_ia['modelo']
            scaler = datos_ia['scaler']
            
        umbral = 0.5 

        X_nuevo = np.array([[
            int(datos['empadronados']), 
            int(datos['votos_validos']), 
            int(datos['votos_blancos']), 
            int(datos['votos_nulos'])
        ]])
        X_scaled = scaler.transform(X_nuevo)
        
        X_pred = modelo.predict(X_scaled)
        error_acta = np.mean(np.power(X_scaled - X_pred, 2))
        
        es_anomala = bool(error_acta > umbral)
        
        if es_anomala:
            riesgo = min(round((error_acta / umbral) * 100, 2), 100.0)
        else:
            riesgo = min(round((error_acta / umbral) * 50, 2), 15.0) 
        
        ActaElectoral.objects.create(
            anio_eleccion=2026,
            codigo_acta=datos.get('codigo_acta', 'SIMULACION-EN-VIVO'),
            canton=datos['canton'],
            parroquia=datos.get('parroquia', 'Demo Parroquia'),
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