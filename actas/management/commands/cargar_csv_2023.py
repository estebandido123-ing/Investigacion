import pandas as pd
import numpy as np
import pickle
from django.core.management.base import BaseCommand
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPRegressor
from actas.models import ActaElectoral

class Command(BaseCommand):
    help = 'Procesa Excel 2023, entrena IA y guarda en la base de datos'

    def add_arguments(self, parser):
        parser.add_argument('ruta_csv', type=str, help='Ruta al archivo Excel del 2023')

    def handle(self, *args, **kwargs):
        ruta_csv = kwargs['ruta_csv']
        self.stdout.write(self.style.WARNING(f"Iniciando procesamiento del archivo: {ruta_csv}..."))
        
        try:
            # 1. Carga y Limpieza
            df = pd.read_excel(ruta_csv)
            df = df.dropna(subset=['CANTON_NOMBRE', 'PARROQUIA_NOMBRE'])
            
            # 2. ETL a nivel de Parroquia
            actas_agrupadas = df.groupby(['CANTON_NOMBRE', 'PARROQUIA_NOMBRE']).agg({
                'VOTOS': 'sum',
                'BLANCOS': 'first',
                'NULOS': 'first'
            }).reset_index()
            
            actas_agrupadas.rename(columns={
                'CANTON_NOMBRE': 'canton',
                'PARROQUIA_NOMBRE': 'parroquia',
                'VOTOS': 'votos_validos',
                'BLANCOS': 'votos_blancos',
                'NULOS': 'votos_nulos'
            }, inplace=True)
            
            actas_agrupadas['empadronados'] = (actas_agrupadas['votos_validos'] + 
                                               actas_agrupadas['votos_blancos'] + 
                                               actas_agrupadas['votos_nulos'])
            
            # 3. Estandarización y Entrenamiento
            X = actas_agrupadas[['empadronados', 'votos_validos', 'votos_blancos', 'votos_nulos']].values
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            modelo_ia = MLPRegressor(hidden_layer_sizes=(8, 4, 8), activation='relu', solver='adam', max_iter=500, random_state=42)
            modelo_ia.fit(X_scaled, X_scaled)
            
            X_pred = modelo_ia.predict(X_scaled)
            mse_por_acta = np.mean(np.power(X_scaled - X_pred, 2), axis=1)
            umbral = float(np.percentile(mse_por_acta, 95))
            
            # 4. Guardar Modelos .pkl
            with open('modelo_ia.pkl', 'wb') as f:
                pickle.dump(modelo_ia, f)
            with open('scaler_ia.pkl', 'wb') as f:
                pickle.dump(scaler, f)
            with open('umbral_ia.pkl', 'wb') as f:
                pickle.dump(umbral, f)
                
            # 5. GUARDAR EN BASE DE DATOS
            self.stdout.write(self.style.WARNING("Guardando registros en la base de datos para visualización..."))
            
            ActaElectoral.objects.filter(anio_eleccion=2023).delete()
            
            for index, row in actas_agrupadas.iterrows():
                X_row = scaler.transform([[row['empadronados'], row['votos_validos'], row['votos_blancos'], row['votos_nulos']]])
                X_pred_row = modelo_ia.predict(X_row)
                mse_row = float(np.mean(np.power(X_row - X_pred_row, 2)))
                
                es_anomala = bool(mse_row > umbral)
                riesgo = min(round((mse_row / umbral) * 100, 2), 100.0) if es_anomala else min(round((mse_row / umbral) * 50, 2), 15.0)

                ActaElectoral.objects.create(
                    anio_eleccion=2023,
                    codigo_acta=f"2023-{str(row['canton'])[:3]}-{str(row['parroquia'])[:3]}-{index}".upper(),
                    canton=row['canton'],
                    parroquia=row['parroquia'],
                    zona="CONSOLIDADO",
                    junta="PARROQUIA",
                    empadronados=row['empadronados'],
                    votos_validos=row['votos_validos'],
                    votos_blancos=row['votos_blancos'],
                    votos_nulos=row['votos_nulos'],
                    es_anomala=es_anomala,
                    porcentaje_riesgo=riesgo
                )
                
            self.stdout.write(self.style.SUCCESS("¡Datos de 2023 listos en la base de datos!"))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error crítico en el procesamiento: {str(e)}"))