import pandas as pd

# Leemos el archivo oficial sin saltarnos ninguna fila
df = pd.read_excel('2021_presidentes_1v.xlsx', nrows=5)

print("\n--- DIAGNÓSTICO DE COLUMNAS ---")
print(df.columns.tolist())