import pandas as pd
import numpy as np
import joblib
from django.core.management.base import BaseCommand
from actas.models import ActaElectoral
from sklearn.preprocessing import MinMaxScaler
from sklearn.neural_network import MLPRegressor

class Command(BaseCommand):
    help = 'Entrena el Autoencoder y audita las actas en la base de datos'

    def handle(self, *args, **kwargs):
        self.stdout.write('Iniciando extracción de datos...')
        
        actas = ActaElectoral.objects.all().values(
            'id', 'empadronados', 'votos_validos', 'votos_blancos', 'votos_nulos'
        )
        df = pd.DataFrame(actas)

        if df.empty:
            self.stdout.write(self.style.ERROR('No hay actas para analizar.'))
            return

        X = df[['empadronados', 'votos_validos', 'votos_blancos', 'votos_nulos']].values

        scaler = MinMaxScaler()
        X_scaled = scaler.fit_transform(X)

        self.stdout.write('Construyendo y entrenando la Red Neuronal (Autoencoder con MLP)...')

        autoencoder = MLPRegressor(
            hidden_layer_sizes=(2,), 
            activation='relu', 
            solver='adam', 
            max_iter=500, 
            random_state=42
        )

        autoencoder.fit(X_scaled, X_scaled)

        self.stdout.write('Calculando anomalías...')

        X_pred = autoencoder.predict(X_scaled)
        mse = np.mean(np.power(X_scaled - X_pred, 2), axis=1)
        umbral = np.percentile(mse, 95)

        actas_actualizadas = []
        for index, row in df.iterrows():
            acta = ActaElectoral.objects.get(id=row['id'])
            error_acta = mse[index]
            
            acta.es_anomala = bool(error_acta > umbral)
            riesgo = (error_acta / np.max(mse)) * 100
            acta.porcentaje_riesgo = round(riesgo, 2)
            
            actas_actualizadas.append(acta)

        ActaElectoral.objects.bulk_update(actas_actualizadas, ['es_anomala', 'porcentaje_riesgo'])

        # AQUÍ ES DONDE SE GUARDA EL MODELO (al final, cuando ya existe)
        joblib.dump(autoencoder, 'modelo_ia.pkl')
        joblib.dump(scaler, 'scaler_ia.pkl')
        joblib.dump(umbral, 'umbral_ia.pkl')

        self.stdout.write(self.style.SUCCESS(f'¡Auditoría completada exitosamente! El umbral de error fue: {umbral:.4f}'))