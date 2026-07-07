import os
import pickle
import numpy as np
from django.core.management.base import BaseCommand
from actas.models import ActaElectoral
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler

class Command(BaseCommand):
    help = 'Entrena el Autoencoder con datos históricos y audita las actas (Versión Optimizada).'

    def handle(self, *args, **kwargs):
        self.stdout.write("Extrayendo datos históricos para entrenamiento...")
        
        historico = ActaElectoral.objects.filter(anio_eleccion__lt=2025)
        
        if not historico.exists():
            self.stdout.write(self.style.WARNING("No hay suficientes datos históricos para entrenar."))
            return

        X_train = np.array([[a.empadronados, a.votos_validos, a.votos_blancos, a.votos_nulos] for a in historico])
        
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)

        self.stdout.write("Entrenando Red Neuronal (Autoencoder)...")
        autoencoder = MLPRegressor(hidden_layer_sizes=(8, 4, 8), activation='relu', max_iter=1000, random_state=42)
        autoencoder.fit(X_train_scaled, X_train_scaled)

        os.makedirs('actas/models', exist_ok=True)
        with open('actas/models/modelo_auditoria.pkl', 'wb') as f:
            pickle.dump({'modelo': autoencoder, 'scaler': scaler}, f)
        
        self.stdout.write(self.style.SUCCESS("¡Modelo entrenado y guardado exitosamente!"))

        # --- AQUÍ ESTÁ LA OPTIMIZACIÓN ---
        self.stdout.write("Auditando base de datos completa y aplicando escritura por lotes (bulk_update)...")
        
        # Cargamos todas las actas en memoria
        todas_las_actas = list(ActaElectoral.objects.all())
        actas_actualizadas = []
        
        for acta in todas_las_actas:
            X_test = np.array([[acta.empadronados, acta.votos_validos, acta.votos_blancos, acta.votos_nulos]])
            X_test_scaled = scaler.transform(X_test)
            
            reconstruccion = autoencoder.predict(X_test_scaled)
            mse = np.mean(np.power(X_test_scaled - reconstruccion, 2))
            
            umbral = 0.5 
            
            if mse > umbral:
                acta.es_anomala = True
                acta.porcentaje_riesgo = min(round((mse / umbral) * 100, 2), 100.0)
            else:
                acta.es_anomala = False
                acta.porcentaje_riesgo = min(round((mse / umbral) * 50, 2), 15.0)
                
            # Agregamos el acta modificada a nuestra lista en lugar de guardar una por una
            actas_actualizadas.append(acta)

        # Ejecutamos una sola consulta gigante a la base de datos
        ActaElectoral.objects.bulk_update(actas_actualizadas, ['es_anomala', 'porcentaje_riesgo'], batch_size=500)

        self.stdout.write(self.style.SUCCESS(f"¡Auditoría finalizada en tiempo récord! Se procesaron {len(actas_actualizadas)} actas."))