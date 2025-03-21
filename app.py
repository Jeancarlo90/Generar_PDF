import io
import zipfile
import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# 📌 Estilos personalizados de Streamlit
st.set_page_config(page_title="Generador de Reportes", page_icon="📄", layout="centered")

# 📌 CSS personalizado para mejorar la apariencia
st.markdown("""
    <style>
        .stButton button {
            background-color: #007BFF;
            color: white;
            font-size: 18px;
            padding: 10px;
            border-radius: 10px;
            width: 100%;
            transition: 0.3s;
        }
        .stButton button:hover {
            background-color: #0056b3;
        }
        .title {
            text-align: center;
            font-size: 36px;
            color: #2C3E50;
            font-weight: bold;
        }
        .subtitle {
            text-align: center;
            font-size: 18px;
            color: #7F8C8D;
        }
    </style>
""", unsafe_allow_html=True)

def generar_pdf(datos):
    """Genera un PDF en memoria con los datos académicos por periodo académico."""
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elementos = []
    estilos = getSampleStyleSheet()

    # 📌 Título del reporte
    titulo = Paragraph("Reporte Académico del Estudiante", estilos["Title"])
    elementos.append(titulo)
    elementos.append(Spacer(1, 12))

    if not datos:
        elementos.append(Paragraph("No hay datos disponibles.", estilos["BodyText"]))
    else:
        # 📌 Crear encabezados, incluyendo el periodo académico
        encabezados = ["PERÍODO ACADÉMICO", "NIVEL", "CURSO", "PLAN", "NOMBRE DE CURSO", "NOTA", "CRÉDITO"]
        contenido_tabla = [encabezados]

        for item in datos:
            fila = [
                item.get("PERIODO_ACADEMICO", ""),  # Añadir periodo académico
                item.get("COD_NIVEL", ""),  
                item.get("COD_MATERIA", ""),  
                item.get("COD_PLAN_ESTUDIO", ""),  
                item.get("NOM_MATERIA", ""),  
                item.get("NOTA", ""),  
                item.get("UNI_CREDITO", item.get("UNI_TEORICA", ""))  
            ]
            contenido_tabla.append(fila)
        
        tabla = Table(contenido_tabla, colWidths=[100, 60, 80, 80, 200, 60, 60])
        tabla.setStyle(TableStyle([ 
            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
            ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        elementos.append(tabla)

    # 📌 Pie de página
    elementos.append(Spacer(1, 50))
    pie_pagina = Paragraph(
        "Av. Honorio Delgado 430, Urbanización Ingeniería, San Martín de Porres<br/>"
        '<a href="http://www.upch.edu.pe">http://www.upch.edu.pe</a>',
        estilos["BodyText"]
    )
    elementos.append(pie_pagina)

    doc.build(elementos)
    
    return buffer.getvalue()


def descargar_zip(datos):
    """Genera un ZIP con el PDF en memoria y permite su descarga."""
    
    pdf_bytes = generar_pdf(datos)
    
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr("reporte.pdf", pdf_bytes)

    zip_buffer.seek(0)
    return zip_buffer


# 📌 Interfaz en Streamlit mejorada
st.markdown('<p class="title">📄 Generador de Reportes en PDF</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Crea y descarga un reporte académico en formato PDF dentro de un archivo ZIP.</p>', unsafe_allow_html=True)
st.write("---")

# 📌 Solicitar el periodo académico como entrada
periodo_academico = st.text_input("Ingrese el Periodo Académico:", value="2025-1")

if st.button("📥 Generar y Descargar ZIP"):
    with st.spinner("Generando reporte... 🛠️"):
        # Datos de ejemplo con periodo académico
        datos = [
            {"PERIODO_ACADEMICO": periodo_academico, "COD_NIVEL": "01", "COD_MATERIA": "MAT101", "COD_PLAN_ESTUDIO": "2025", 
             "NOM_MATERIA": "Matemáticas Avanzadas", "NOTA": "18", "UNI_CREDITO": "4"},
            {"PERIODO_ACADEMICO": periodo_academico, "COD_NIVEL": "01", "COD_MATERIA": "FIS102", "COD_PLAN_ESTUDIO": "2025", 
             "NOM_MATERIA": "Física General", "NOTA": "17", "UNI_CREDITO": "3"}
        ]

        zip_file = descargar_zip(datos)

        st.success("✅ ¡Reporte generado con éxito!")

        st.download_button(
            label="📂 Descargar Reporte en ZIP",
            data=zip_file,
            file_name="reporte.zip",
            mime="application/zip"
        )
