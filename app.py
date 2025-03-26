# app.py
import streamlit as st
from database import get_connection
from pdf_generator import generate_pdf

# Streamlit app
st.title("Generador de Reporte de Notas")

dni = st.text_input("Ingrese su DNI:")

if st.button("Generar Reporte"):
    connection = get_connection()
    cursor = connection.cursor()

    # Execute the query
    query = """
    SELECT
        A.COD_UNIDAD,
        U.NOM_UNIDAD,
        A.COD_PENSUM,
        T.NUM_IDENTIFICACION,
        T.NOM_LARGO,
        H.ID_ALUM_PROGRAMA,
        H.per_acumula || ' - ' || PE.NOM_PERIODO AS COD_PERIODO,
        PE.FEC_INICIO,
        H.COD_MATERIA,
        NVL(H.COD_MATERIA_E, H.COD_MATERIA) AS OFERTA,
        P.NOM_MATERIA,
        P.NUM_NIVEL,
        P.UNI_TEORICA,
        CASE
            WHEN H.EST_MATERIA = '5' THEN 'RET'
            WHEN P.TIP_NOTA = 'A' AND H.IND_APROBADA = '1' THEN 'APTO'
            WHEN P.TIP_NOTA = 'A' AND H.IND_APROBADA = '0' THEN 'NO APTO'
            ELSE TO_CHAR(H.DEF_HISTORIA, '99.99')
        END AS NOTA,
        R.NUM_CRED,
        R.CRED_APRO_ACUM,
        R.CRED_DESAPRO_ACUM,
        R.CRED_RET,
        R.PROMEDIO_ACUMULADO
    FROM
        sinu.SRC_HIS_ACADEMICA H
        LEFT JOIN sinu.SRC_ALUM_PROGRAMA A ON H.ID_ALUM_PROGRAMA = A.ID_ALUM_PROGRAMA
        INNER JOIN sinu.SRC_UNI_ACADEMICA U ON A.COD_UNIDAD = U.COD_UNIDAD
        INNER JOIN sinu.BAS_TERCERO T ON T.ID_TERCERO = A.ID_TERCERO
        INNER JOIN sinu.SRC_MAT_PENSUM P ON P.COD_UNIDAD = NVL(H.COD_UNI_E, A.COD_UNIDAD)
            AND P.COD_PENSUM = NVL(H.COD_PEN_E, A.COD_PENSUM)
            AND P.COD_MATERIA = NVL(H.COD_MATERIA_E, H.COD_MATERIA)
        INNER JOIN sinu.SRC_ENC_PERIODO PE ON H.PER_ACUMULA = PE.COD_PERIODO
        INNER JOIN (
            SELECT
                A.COD_UNIDAD,
                A.COD_PENSUM,
                T.NUM_IDENTIFICACION,
                T.NOM_LARGO,
                H.ID_ALUM_PROGRAMA,
                SUM(P.UNI_TEORICA) AS NUM_CRED,
                NVL(SUM(CASE WHEN H.IND_APROBADA = '1' THEN P.UNI_TEORICA END), 0) AS CRED_APRO_ACUM,
                NVL(SUM(CASE WHEN H.IND_APROBADA = '0' AND H.EST_MATERIA <> '5' THEN P.UNI_TEORICA END), 0) AS CRED_DESAPRO_ACUM,
                NVL(SUM(CASE WHEN H.EST_MATERIA = '5' THEN P.UNI_TEORICA END), 0) AS CRED_RET,
                TRUNC(SUM(CASE WHEN H.IND_ACUMULA = '1' THEN P.UNI_TEORICA * H.DEF_HISTORIA END) / SUM(CASE WHEN H.IND_ACUMULA = '1' THEN P.UNI_TEORICA END), 3) AS PROMEDIO_ACUMULADO
            FROM
                sinu.SRC_HIS_ACADEMICA H
                LEFT JOIN sinu.SRC_ALUM_PROGRAMA A ON H.ID_ALUM_PROGRAMA = A.ID_ALUM_PROGRAMA
                INNER JOIN sinu.BAS_TERCERO T ON T.ID_TERCERO = A.ID_TERCERO
                INNER JOIN sinu.SRC_MAT_PENSUM P ON P.COD_UNIDAD = NVL(H.COD_UNI_E, A.COD_UNIDAD)
                    AND P.COD_PENSUM = NVL(H.COD_PEN_E, A.COD_PENSUM)
                    AND P.COD_MATERIA = NVL(H.COD_MATERIA_E, H.COD_MATERIA)
            WHERE
                T.NUM_IDENTIFICACION IN (:dni)
                AND A.EST_ALUMNO = '1'
            GROUP BY
                A.COD_UNIDAD,
                A.COD_PENSUM,
                T.NUM_IDENTIFICACION,
                T.NOM_LARGO,
                H.ID_ALUM_PROGRAMA
        ) R ON A.ID_ALUM_PROGRAMA = R.ID_ALUM_PROGRAMA
    WHERE
        T.NUM_IDENTIFICACION IN (:dni)
        AND A.EST_ALUMNO = '1'
    ORDER BY
        T.NUM_IDENTIFICACION,
        PE.FEC_INICIO,
        H.COD_PERIODO,
        P.NUM_NIVEL,
        H.COD_MATERIA;
    """
    cursor.execute(query, dni=dni)
    results = cursor.fetchall()

    # Generate PDF
    data = [
        {
            "NIVEL": row[6],
            "CURSO_PLAN": row[1],
            "CURSO_OFERTA": row[9],
            "NOMBRE_DE_CURSO": row[11],
            "NOTA": row[12],
            "CREDITO": row[10]
        }
        for row in results
    ]

    generate_pdf(data, "reporte_notas.pdf")

    st.success("Reporte generado exitosamente!")
    with open("reporte_notas.pdf", "rb") as file:
        btn = st.download_button(
            label="Descargar Reporte",
            data=file,
            file_name="reporte_notas.pdf",
            mime="application/octet-stream"
        )

    # Close the database connection
    cursor.close()
    connection.close()
