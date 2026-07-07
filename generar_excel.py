import pandas as pd

# 1. Simulamos las primeras 6 filas (índices 0 a 5) que el CNE usa para títulos y logos
filas_vacias = [[""] * 10 for _ in range(6)]
filas_vacias[0][0] = "CONSEJO NACIONAL ELECTORAL"
filas_vacias[1][0] = "REPORTE DE RESULTADOS POR PARROQUIA 2021"

# 2. En la fila 7 (índice 6) colocamos los encabezados exactos del formato
encabezados = ['PROVINCIA', 'CODIGO', 'CANTON', 'COD_CANT', 'PARROQUIA', 'COD_PARR', 'VOTOS/VALIDOS', 'VOTOS/BLANCO', 'VOTOS/NULOS', 'VOTOS/TOTAL.']

# 3. Agregamos datos de prueba realistas para la provincia de Pichincha
datos = [
    ['PICHINCHA', '17', 'QUITO', '1701', 'IÑAQUITO', '170150', 45000, 2000, 1500, 48500],
    ['PICHINCHA', '17', 'QUITO', '1701', 'CALDERON', '170151', 60000, 3000, 2500, 65500],
    ['PICHINCHA', '17', 'MEJIA', '1702', 'MACHACHI', '170250', 25000, 1500, 800, 27300],
    ['PICHINCHA', '17', 'CAYAMBE', '1703', 'AYORA', '170351', 8000, 400, 300, 8700],
    ['PICHINCHA', '17', 'RUMIÑAHUI', '1704', 'SANGOLQUI', '170450', 35000, 1200, 900, 37100],
]

# Unimos todo en un solo DataFrame
df = pd.DataFrame(filas_vacias + [encabezados] + datos)

# Exportamos el archivo Excel (sin índices extra de pandas para respetar el formato original)
nombre_archivo = 'Formato_Parroquias_2021_Llenar.xlsx'
df.to_excel(nombre_archivo, index=False, header=False)

print(f"✅ Archivo '{nombre_archivo}' generado con éxito en la raíz del proyecto.")