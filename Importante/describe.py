import pandas as pd
import glob
import os

#define el path de los archivos 
ruta = os.path.join('oertel_runs', '**', 'summary.csv')
#'**' busca en todas las carpetas por el archivo que se llame summary.csv

#para entontrar los pathnames matching un patron especifico
archivos = glob.glob(ruta, recursive=True)
#recursive=True para que realice la búsqueda en todas las carpetas según '**'

#Leer y juntar todo en un solo dataframe
df = pd.concat((pd.read_csv(f) for f in archivos), ignore_index = True)
#ignore_index=True reinicia la enumeración de cada archivo para juntar los archivos

#guardar sin indices en el .csv
df.to_csv('summary_20k.csv', index=False)

print("se han guardado exitosamente")