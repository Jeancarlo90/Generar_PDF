import io
import zipfile
import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

def generar_pdf(datos):
    """Genera un PDF en memoria con los datos académicos."""
    
    buffer = io.BytesIO()  # 📌 Almacenamiento en memoria
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elementos = []
    estilos = getSampleStyleSheet()

    # 📌 Título del reporte
    titulo = Paragraph("Reporte Académico del Estudiante", estilos["Title"])
    elementos.append(titulo)
    elementos.append(Spacer(1, 12))

    # 📌 Verificar si hay datos
    if not datos:
        elementos.append(Paragraph("No hay datos disponibles.", estilos["BodyText"]))
    else:
        # 📌 Encabezados de la tabla
        encabezados = ["NIVEL", "CURSO", "PLAN", "NOMBRE DE CURSO", "NOTA", "CRÉDITO"]
        contenido_tabla = [encabezados]  # Primera fila con encabezados
        
        # 📌 Llenar la tabla con los datos
        for item in datos:
            fila = [
                item.get("COD_NIVEL", ""),  
                item.get("COD_MATERIA", ""),  
                item.get("COD_PLAN_ESTUDIO", ""),  
                item.get("NOM_MATERIA", ""),  
                item.get("NOTA", ""),  
                item.get("UNI_CREDITO", item.get("UNI_TEORICA", ""))  
            ]
            contenido_tabla.append(fila)
        
        # 📌 Crear tabla
        tabla = Table(contenido_tabla, colWidths=[60, 80, 80, 200, 60, 60])
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

    # 📌 Espaciado antes del pie de página
    elementos.append(Spacer(1, 50))

    # 📌 Pie de página con dirección y enlace
    pie_pagina = Paragraph(
        "Av. Honorio Delgado 430, Urbanización Ingeniería, San Martín de Porres<br/>"
        '<a href="http://www.upch.edu.pe">http://www.upch.edu.pe</a>',
        estilos["BodyText"]
    )
    elementos.append(pie_pagina)

    # 📌 Construcción del PDF en memoria
    doc.build(elementos)
    
    return buffer.getvalue()  # Devuelve el contenido en bytes del PDF


def descargar_zip(datos):
    """Genera un ZIP con el PDF en memoria y permite su descarga."""

    # 📌 Generar el PDF en memoria
    pdf_bytes = generar_pdf(datos)
    
    # 📌 Crear un ZIP en memoria
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr("reporte.pdf", pdf_bytes)  # 📌 Guardar el PDF en el ZIP

    zip_buffer.seek(0)  # 📌 Mover el puntero al inicio para la descarga

    return zip_buffer


# 📌 Interfaz en Streamlit
st.title("Generador de Reportes en PDF")

# 📌 Verificar si hay datos antes de intentar generar el reporte
datos = [
    {"COD_NIVEL": "01", "COD_MATERIA": "MAT101", "COD_PLAN_ESTUDIO": "2025", 
     "NOM_MATERIA": "Matemáticas Avanzadas", "NOTA": "18", "UNI_CREDITO": "4"},
    {"COD_NIVEL": "01", "COD_MATERIA": "FIS102", "COD_PLAN_ESTUDIO": "2025", 
     "NOM_MATERIA": "Física General", "NOTA": "17", "UNI_CREDITO": "3"}
]

if not datos:
    st.warning("⚠️ No se encontraron datos para generar el reporte.")
else:
    # 📌 Barra de progreso
    with st.spinner("Generando archivo..."):
        zip_file = descargar_zip(datos)

        # 📌 Descargar el ZIP en Streamlit
        st.download_button(
            label="Descargar Reporte en ZIP 📂",
            data=zip_file,
            file_name="reporte.zip",
            mime="application/zip"
        )
