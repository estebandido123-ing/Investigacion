import pandas as pd

# Cambia 'tu_archivo.csv' por el nombre real de tu archivo
nombre_archivo = '2023_anticipadas_1v.xlsx'

try:
    # Probamos con punto y coma (;) que es lo estándar en Ecuador, 
    # si da error, cambia sep=';' por sep=','
    df = pd.read_excel(nombre_archivo, nrows=5)
    
    print("--- Nombres de las columnas ---")
    print(df.columns.tolist())
    
except Exception as e:
    print(f"Error al leer el archivo: {e}")