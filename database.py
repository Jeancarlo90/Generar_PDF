import os
import cx_Oracle
from dotenv import load_dotenv

# Cargar variables de entorno desde un archivo .env
load_dotenv()

# Configuración de conexión desde variables de entorno
DB_HOST = os.getenv("DB_HOST", "172.17.100.122")
DB_PORT = os.getenv("DB_PORT", 1521)
DB_SERVICE = os.getenv("DB_SERVICE", "UPCHP")
DB_USER = os.getenv("DB_USER", "USR_IURQUIAGA")
DB_PASSWORD = os.getenv("DB_PASSWORD", "Y6F3n2%G")

def conectar_oracle():
    """Establece conexión con la base de datos Oracle."""
    try:
        dsn = cx_Oracle.makedsn(DB_HOST, DB_PORT, service_name=DB_SERVICE)
        conexion = cx_Oracle.connect(user=DB_USER, password=DB_PASSWORD, dsn=dsn)
        return conexion
    except cx_Oracle.Error as e:
        error, = e.args  # Desempaquetar el error
        print(f"❌ Error de conexión a Oracle: {error.message}")
        return None

def obtener_datos(num_identificacion):
    """Obtiene datos desde Oracle para un estudiante en específico."""
    conexion = conectar_oracle()
    if not conexion:
        return []

    try:
        with conexion.cursor() as cursor:
            query = f"""
            SELECT A.COD_UNIDAD, U.NOM_UNIDAD, A.COD_PENSUM, T.NUM_IDENTIFICACION, T.NOM_LARGO, 
                   H.ID_ALUM_PROGRAMA, H.per_acumula || ' - ' || PE.NOM_PERIODO AS COD_PERIODO, 
                   PE.FEC_INICIO, H.COD_MATERIA, NVL(H.COD_MATERIA_E, H.COD_MATERIA) AS OFERTA, 
                   P.NOM_MATERIA, P.NUM_NIVEL, P.UNI_TEORICA, 
                   CASE 
                       WHEN H.EST_MATERIA = '5' THEN 'RET' 
                       WHEN P.TIP_NOTA = 'A' AND H.IND_APROBADA = '1' THEN 'APTO'
                       WHEN P.TIP_NOTA = 'A' AND H.IND_APROBADA = '0' THEN 'NO APTO'
                       ELSE TO_CHAR(H.DEF_HISTORIA, '99.99') 
                   END AS NOTA
            FROM sinu.SRC_HIS_ACADEMICA H
            LEFT JOIN sinu.SRC_ALUM_PROGRAMA A ON H.ID_ALUM_PROGRAMA = A.ID_ALUM_PROGRAMA
            INNER JOIN sinu.SRC_UNI_ACADEMICA U ON A.COD_UNIDAD = U.COD_UNIDAD
            INNER JOIN sinu.BAS_TERCERO T ON T.ID_TERCERO = A.ID_TERCERO
            INNER JOIN sinu.SRC_MAT_PENSUM P 
                ON P.COD_UNIDAD = NVL(H.COD_UNI_E, A.COD_UNIDAD)
                AND P.COD_PENSUM = NVL(H.COD_PEN_E, A.COD_PENSUM)
                AND P.COD_MATERIA = NVL(H.COD_MATERIA_E, H.COD_MATERIA)
            INNER JOIN sinu.SRC_ENC_PERIODO PE ON H.PER_ACUMULA = PE.COD_PERIODO
            WHERE T.NUM_IDENTIFICACION = :num_identificacion
              AND A.EST_ALUMNO = '1'
            ORDER BY T.NUM_IDENTIFICACION, PE.FEC_INICIO, H.COD_PERIODO, P.NUM_NIVEL, H.COD_MATERIA
            """
            
            cursor.execute(query, num_identificacion=num_identificacion)
            
            # Verifica si hay datos antes de obtener columnas
            if cursor.description is None:
                print("⚠️ La consulta no devolvió resultados.")
                return []

            columnas = [col[0] for col in cursor.description]
            datos = [dict(zip(columnas, row)) for row in cursor.fetchall()]
            return datos

    except cx_Oracle.Error as e:
        error, = e.args
        print(f"❌ Error en la consulta: {error.message}")
        return []
    finally:
        conexion.close()

# Ejemplo de uso
if __name__ == "__main__":
    estudiante = "76735491"  # Cambiar por cualquier número de identificación
    resultado = obtener_datos(estudiante)
    
    if resultado:
        for fila in resultado:
            print(fila)
    else:
        print("No se encontraron datos.")
