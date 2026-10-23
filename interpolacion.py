import os
import sys

# 1. INICIALIZAR EL ENTORNO CORE DE QGIS (Requerido para VS Code)
# Ajustamos las rutas nativas según tu versión 3.44 de QGIS LTR
os.environ['QT_QPA_PLATFORM'] = 'offscreen' # Evita que intente abrir ventanas visuales
sys.path.append(r'C:\Program Files\QGIS 3.44.15\apps\qgis-ltr\python')
sys.path.append(r'C:\Program Files\QGIS 3.44.15\apps\qgis-ltr\python\plugins')

from qgis.core import QgsApplication
# Inicializar aplicación QGIS sin entorno gráfico (True = Sin interfaz)
qgis_app = QgsApplication([], True)
qgis_app.initQgis()

# Importamos processing después de haber inicializado QGIS
import processing
from processing.core.Processing import Processing
Processing.initialize()

# 2. CONFIGURACIÓN DE RUTAS Y PROCESAMIENTO
ruta_base = r"C:\Users\santiago.negrete\Downloads\x"
carpeta_csv = os.path.join(ruta_base, "datos_xyz_extraidos")
carpeta_raster = os.path.join(ruta_base, "rasters_interpolados")

if not os.path.exists(carpeta_csv): os.makedirs(carpeta_csv)
if not os.path.exists(carpeta_raster): os.makedirs(carpeta_raster)

nombres_base = ["E1_44", "E1_45", "E1_46", "E1_47", "E1_48"]
crs_destino = "EPSG:25832"
pixel_size = 0.2

print("--- Iniciando proceso desde VS Code ---")

for nombre in nombres_base:
    ruta_2dm = os.path.join(ruta_base, f"{nombre}.2dm")
    ruta_csv = os.path.join(carpeta_csv, f"{nombre}_xyz.csv")
    ruta_raster_salida = os.path.join(carpeta_raster, f"{nombre}_interpolado.tif")
    
    # Extracción de Nodos XYZ
    if os.path.exists(ruta_2dm) and not os.path.exists(ruta_csv):
        print(f"Extrayendo {nombre}.2dm...")
        nodos = 0
        with open(ruta_2dm, 'r', encoding='utf-8', errors='ignore') as f_in, open(ruta_csv, 'w', encoding='utf-8') as f_out:
            f_out.write("X,Y,Z\n")
            for linea in f_in:
                partes = linea.split()
                if partes and partes[0] == "ND" and len(partes) >= 5:
                    f_out.write(f"{partes[2]},{partes[3]},{partes[4]}\n")
                    nodos += 1
        print(f"✔ Nodos guardados en CSV: {nodos}")

    # Interpolación Nativa Externa
    if os.path.exists(ruta_csv):
        ruta_limpia = ruta_csv.replace("\\", "/")
        # Leemos el archivo CSV usando el proveedor de texto estructurado
        from qgis.core import QgsVectorLayer
        uri = f"file:///{ruta_limpia}?type=csv&xField=X&yField=Y&spatialIndex=no&subsetIndex=no&watchFile=no&crs={crs_destino}"
        capa_puntos = QgsVectorLayer(uri, f"puntos_{nombre}", "delimitedtext")
        
        if capa_puntos.isValid():
            ext = capa_puntos.extent()
            str_extent = f"{ext.xMinimum()},{ext.xMaximum()},{ext.yMinimum()},{ext.yMaximum()} [{crs_destino}]"
            datos_interpolacion = f"{ruta_limpia}::~::0::~::2::~::0"
            
            parametros = {
                'INTERPOLATION_DATA': datos_interpolacion,
                'DISTANCE_COEFFICIENT': 2,
                'EXTENT': str_extent,
                'PIXEL_SIZE': pixel_size,
                'OUTPUT': ruta_raster_salida
            }
            
            try:
                print(f"Interpolando cuadrante {nombre} a 0.2m...")
                processing.run("qgis:idwinterpolation", parametros)
                if os.path.exists(ruta_raster_salida):
                    print(f"⭐⭐ ¡Procesado con éxito!: {nombre}_interpolado.tif")
            except Exception as e:
                print(f"❌ Error al procesar {nombre}: {str(e)}")
        else:
            print(f"❌ Error: La capa de puntos no es válida en {nombre}")

# 3. CERRAR EL ENTORNO SEGURO DE QGIS
print("Cerrando entorno de QGIS de forma segura...")
qgis_app.exitQgis()
print("--- Proceso completado en disco ---")
