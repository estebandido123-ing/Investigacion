import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from actas.models import ActaElectoral

class Command(BaseCommand):
    help = 'Genera actas electorales sintéticas para la provincia de Pichincha (2025-2026)'

    def handle(self, *args, **kwargs):
        self.stdout.write('Eliminando datos anteriores...')
        ActaElectoral.objects.all().delete()

        cantones = ['Quito', 'Cayambe', 'Mejía', 'Rumiñahui', 'Pedro Moncayo', 'San Miguel de los Bancos']
        actas_a_crear = []
        fecha_base = timezone.now() - timedelta(days=5)

        self.stdout.write('Generando 500 actas nuevas...')

        for i in range(1, 501):
            empadronados = random.randint(250, 350) # Promedio de personas por junta
            
            # Simulamos que un 5% de las actas tienen fraude o errores de tipeo
            es_fraude = random.random() < 0.05 

            if es_fraude:
                # Anomalía matemática: Más votos que empadronados
                votos_validos = empadronados + random.randint(10, 50)
                blancos = random.randint(0, 10)
                nulos = random.randint(0, 15)
            else:
                # Comportamiento normal: Abstencionismo del 20% aprox
                votantes_reales = int(empadronados * random.uniform(0.7, 0.9))
                blancos = random.randint(0, 15)
                nulos = random.randint(0, 20)
                votos_validos = votantes_reales - blancos - nulos

            acta = ActaElectoral(
                codigo_acta=f"PICH-{2025}-{str(i).zfill(4)}",
                canton=random.choice(cantones),
                parroquia=f"Parroquia_{random.randint(1, 20)}",
                zona=f"Zona_{random.randint(1, 5)}",
                junta=f"{random.randint(1, 10)}{random.choice(['M', 'F'])}",
                empadronados=empadronados,
                votos_validos=votos_validos,
                votos_blancos=blancos,
                votos_nulos=nulos,
                hora_ingreso=fecha_base + timedelta(minutes=random.randint(1, 2880)) # Ingresos distribuidos en 48 horas
            )
            actas_a_crear.append(acta)

        # Usamos bulk_create para guardar todo en la base de datos de un solo golpe (más eficiente)
        ActaElectoral.objects.bulk_create(actas_a_crear)
        
        self.stdout.write(self.style.SUCCESS('¡Éxito! Se han creado 500 actas en la base de datos.'))