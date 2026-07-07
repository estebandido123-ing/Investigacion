import pandas as pd
from django.core.management.base import BaseCommand
from actas.models import ActaElectoral
from django.utils import timezone

class Command(BaseCommand):
    help = 'Ingesta masiva, limpieza y consolidación de datos oficiales del CNE'

    def add_arguments(self, parser):
        parser.add_argument('archivo_excel', type=str)
        parser.add_argument('anio', type=int)

    def handle(self, *args, **kwargs):
        ruta = kwargs['archivo_excel']
        anio = kwargs['anio']

        self.stdout.write(f"Iniciando lectura de la base de datos oficial: {ruta}...")

        try:
            # 1. Leemos el archivo completo (ahora sin saltar filas)
            df = pd.read_excel(ruta, engine='openpyxl')
            df.columns = df.columns.str.strip() # Limpiamos espacios en los encabezados

            self.stdout.write("Filtrando la provincia objetivo y agrupando candidatos por acta...")

            # 2. Optimizamos memoria: Filtramos exclusivamente PICHINCHA
            df['PROVINCIA_NOMBRE'] = df['PROVINCIA_NOMBRE'].fillna('').astype(str)
            df_pichincha = df[df['PROVINCIA_NOMBRE'].str.strip().str.upper() == 'PICHINCHA']

            if df_pichincha.empty:
                self.stdout.write(self.style.WARNING("No se encontraron registros de PICHINCHA en este archivo."))
                return

            # 3. Agrupamos las filas por Junta/Acta para consolidar los votos de todos los candidatos
            columnas_agrupacion = [
                'ACTA_CODIGO', 'CANTON_NOMBRE', 'PARROQUIA_NOMBRE', 
                'ZONA_NOMBRE', 'JUNTA_CODIGO', 'ELECTORES', 'BLANCOS', 'NULOS'
            ]
            
            # Al agrupar, sumamos la columna 'VOTOS_CANDIDATO' para tener el total de Válidos
            df_actas = df_pichincha.groupby(columnas_agrupacion, dropna=False)['VOTOS_CANDIDATO'].sum().reset_index()

            actas_a_crear = []
            
            for _, row in df_actas.iterrows():
                # Validación de seguridad para campos de texto
                zona_str = str(row['ZONA_NOMBRE']).strip()
                if zona_str == 'nan': zona_str = "NO ESPECIFICADA"

                actas_a_crear.append(ActaElectoral(
                    anio_eleccion=anio,
                    codigo_acta=str(row['ACTA_CODIGO']).strip(),
                    canton=str(row['CANTON_NOMBRE']).strip(),
                    parroquia=str(row['PARROQUIA_NOMBRE']).strip(),
                    zona=zona_str[:50], 
                    junta=str(row['JUNTA_CODIGO']).strip()[:20],
                    empadronados=int(row['ELECTORES']),
                    votos_validos=int(row['VOTOS_CANDIDATO']), # Aquí está la suma de todos los candidatos
                    votos_blancos=int(row['BLANCOS']),
                    votos_nulos=int(row['NULOS']),
                    hora_ingreso=timezone.now()
                ))
            
            self.stdout.write("Guardando en la base de datos (esto puede tomar unos segundos)...")
            # Inserción masiva optimizada
            ActaElectoral.objects.bulk_create(actas_a_crear, ignore_conflicts=True)
            
            self.stdout.write(self.style.SUCCESS(f'¡Éxito total! Se procesaron y guardaron {len(actas_a_crear)} actas consolidadas para el año {anio}.'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error crítico durante el procesamiento: {str(e)}'))