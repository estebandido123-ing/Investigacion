import csv
from django.core.management.base import BaseCommand
from actas.models import ActaElectoral
from django.utils import timezone

class Command(BaseCommand):
    help = 'Carga datos históricos reales del CNE desde un archivo CSV'

    def add_arguments(self, parser):
        parser.add_argument('archivo_csv', type=str, help='Ruta al archivo CSV (ej. pichincha_2021.csv)')
        parser.add_argument('anio', type=int, help='Año de la elección correspondiente a estos datos')

    def handle(self, *args, **kwargs):
        ruta_archivo = kwargs['archivo_csv']
        anio = kwargs['anio']

        self.stdout.write(f"Iniciando carga masiva de datos para el año {anio}...")

        try:
            with open(ruta_archivo, mode='r', encoding='utf-8-sig') as file:
                reader = csv.DictReader(file)
                actas_a_crear = []
                
                for i, row in enumerate(reader):
                    # Generamos un código de acta único combinando el año y un iterador si el CSV no trae uno
                    cod_acta = row.get('CODIGO_ACTA', f"ACT-{anio}-{row['CANTON'][:3].upper()}-{i}")

                    actas_a_crear.append(ActaElectoral(
                        anio_eleccion=anio,
                        codigo_acta=cod_acta,
                        canton=row['CANTON'],
                        parroquia=row['PARROQUIA'],
                        zona=row.get('ZONA', 'Sin Zona'),
                        junta=row['JUNTA'],
                        empadronados=int(row['EMPADRONADOS']),
                        votos_validos=int(row['VALIDOS']),
                        votos_blancos=int(row['BLANCOS']),
                        votos_nulos=int(row['NULOS']),
                        hora_ingreso=timezone.now()
                    ))
                
                # Inserción masiva para optimizar el rendimiento (vital cuando son miles de registros)
                ActaElectoral.objects.bulk_create(actas_a_crear, ignore_conflicts=True)
                
                self.stdout.write(self.style.SUCCESS(f'¡Éxito! Se procesaron {len(actas_a_crear)} actas del {anio} en la base de datos.'))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'Error: No se encontró el archivo en la ruta {ruta_archivo}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error inesperado durante la carga: {str(e)}'))