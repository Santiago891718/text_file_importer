import os
import sys

# =====================================================================
# CONFIGURACIÓN DE ENTORNO NATIVO DE QGIS E INYECCIÓN DE RUTA
# =====================================================================
os.environ["PYTHONNOUSERSITE"] = "1"
sys.path = [p for p in sys.path if "AppData\\Roaming\\Python" not in p]

# Inyección para rescatar rioxarray de la carpeta de usuario
ruta_usuario_librerias = r"C:\Users\santiago.negrete\AppData\Roaming\Python\Python312\site-packages"
if ruta_usuario_librerias not in sys.path:
    sys.path.append(ruta_usuario_librerias)

os.environ["PROJ_DATA"] = r"C:\Program Files\QGIS 3.34.14\share\proj"
os.environ["PROJ_LIB"] = r"C:\Program Files\QGIS 3.34.14\share\proj"
os.environ["GDAL_DATA"] = r"C:\Program Files\QGIS 3.34.14\share\gdal"

qgis_bin = r"C:\Program Files\QGIS 3.34.14\bin"
if qgis_bin not in os.environ["PATH"]:
    os.environ["PATH"] = qgis_bin + os.path.pathsep + os.environ["PATH"]

# =====================================================================
# IMPORTACIÓN DE LIBRERÍAS
# =====================================================================
import pandas as pd
import geopandas as gpd
import numpy as np
import rioxarray
import xarray as xr
from shapely.geometry import Point
from scipy.spatial import cKDTree

# =====================================================================
# CONFIGURACIÓN DE RUTAS Y PARÁMETROS
# =====================================================================
CARPETA_ORIGEN = r"J:\Santiago_N"
CARPETA_DESTINO = r"C:\Users\santiago.negrete\Downloads\x"

archivos_2dm = ["E1_44.2dm", "E1_45.2dm", "E1_46.2dm", "E1_47.2dm", "E1_48.2dm"]
RUTA_VECTOR = os.path.join(CARPETA_DESTINO, "puntos_3d.gpkg")
RUTA_RASTER = os.path.join(CARPETA_DESTINO, "raster_interpolado.tif")

RESOLUCION_CELDA = 2.0  # Tamaño del píxel en metros
CRS_DATOS = "EPSG:25832"

if not os.path.exists(CARPETA_DESTINO):
    os.makedirs(CARPETA_DESTINO)

# =====================================================================
# 1. EXTRACCIÓN DE PUNTOS
# =====================================================================
todos_los_puntos = []
print("--- FASE 1: Extrayendo puntos desde los archivos 2DM ---")
for archivo in archivos_2dm:
    ruta_completa = os.path.join(CARPETA_ORIGEN, archivo)
    if not os.path.exists(ruta_completa):
        print(f"⚠️ Saltando (no encontrado): {archivo}")
        continue
    
    print(f"Leyendo {archivo}...")
    with open(ruta_completa, 'r', encoding='utf-8', errors='ignore') as f:
        for linea in f:
            if linea.startswith("ND "):
                partes = linea.split()
                if len(partes) >= 5:
                    try:
                        todos_los_puntos.append({
                            'X': float(partes[2]),
                            'Y': float(partes[3]),
                            'Z': float(partes[4])
                        })
                    except ValueError:
                        continue

df = pd.DataFrame(todos_los_puntos).drop_duplicates(subset=['X', 'Y'], keep='first')
print(f"Puntos únicos válidos cargados: {len(df)}")

# =====================================================================
# 2. CREACIÓN Y GUARDADO DEL VECTOR (XYZ en EPSG:25832)
# =====================================================================
print("\n--- FASE 2: Creando y guardando archivo vectorial (GPKG) ---")
geometrias_3d = [Point(xyz) for xyz in zip(df['X'], df['Y'], df['Z'])]
gdf = gpd.GeoDataFrame(df, geometry=geometrias_3d, crs=CRS_DATOS)

# CORRECCIÓN DE MOTOR: Forzamos el uso de pyogrio nativo sin usar el driver Arrow conflictivo
gdf.to_file(RUTA_VECTOR, driver="GPKG", layer="puntos_z_25832", engine="pyogrio", use_arrow=False)
print(f"✅ Vector guardado con éxito en: {RUTA_VECTOR}")

# =====================================================================
# 3. INTERPOLACIÓN ESPACIAL POR KDTREE (ALTA VELOCIDAD Y BAJO CONSUMO)
# =====================================================================
print("\n--- FASE 3: Interpolando puntos para generar el Raster (Algoritmo Big Data) ---")

x_coords = df['X'].values
y_coords = df['Y'].values
z_values = df['Z'].values

x_min, x_max = x_coords.min() - RESOLUCION_CELDA, x_coords.max() + RESOLUCION_CELDA
y_min, y_max = y_coords.min() - RESOLUCION_CELDA, y_coords.max() + RESOLUCION_CELDA

x_range = np.arange(x_min, x_max, RESOLUCION_CELDA)
y_range = np.arange(y_max, y_min, -RESOLUCION_CELDA)
grid_x, grid_y = np.meshgrid(x_range, y_range)

grid_points = np.c_[grid_x.ravel(), grid_y.ravel()]

print("Construyendo árbol indexado espacial KDTree...")
tree = cKDTree(np.c_[x_coords, y_coords])

print("Calculando distancias e interpolando celdas mediante IDW (Ponderación Inversa)...")
distancias, indices = tree.query(grid_points, k=4, workers=-1)

weights = 1.0 / np.maximum(distancias, 1e-6)**2
z_interpolado = np.sum(weights * z_values[indices], axis=1) / np.sum(weights, axis=1)

grid_z = z_interpolado.reshape(grid_x.shape)

da_raster = xr.DataArray(
    grid_z,
    dims=["y", "x"],
    coords={"y": y_range, "x": x_range}
)

da_raster = da_raster.rio.write_crs(CRS_DATOS)
da_raster = da_raster.rio.write_nodata(-9999.0, encoded=True)

print("Escribiendo archivo GeoTIFF final en disco...")
da_raster.rio.to_raster(RUTA_RASTER)

print(f"✅ Raster exportado con éxito en: {RUTA_RASTER}")
print("\n🎉 ¡Proceso masivo completado con éxito!")
