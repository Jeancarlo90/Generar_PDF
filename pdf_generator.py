# pdf_generator.py
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from datetime import datetime

def generate_pdf(data, filename, student_info, logo_path):
    try:
        c = canvas.Canvas(filename, pagesize=letter)
        width, height = letter

        # Insertar el logotipo
        logo = ImageReader(logo_path)
        c.drawImage(logo_path, 50, height - 120, width=100, height=100)

        # Información del estudiante
        c.setFont("Helvetica-Bold", 12)
        c.drawCentredString(width / 2, height - 50, "FICHA DE NOTAS")
        c.setFont("Helvetica", 11)
        c.drawString(200, height - 70, student_info['name'])
        c.drawString(200, height - 90, f"DNI: {student_info['dni']}")
        c.drawString(200, height - 110, student_info['career'])

        # Fecha y hora
        now = datetime.now().strftime("%d.%m.%Y %I:%M %p")
        c.setFont("Helvetica", 10)
        c.drawString(width - 200, height - 50, now)

        y = height - 140  # Posición inicial debajo de la info del estudiante

        # Iterar sobre los periodos académicos
        page_number = 1
        for period, courses in data.items():
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, y, f"PERIODO ACADÉMICO: {period}")
            y -= 30  # Más espacio entre el título y la tabla

            # Dibujar encabezado de la tabla
            headers = ["NIVEL", "CURSO PLAN", "NOMBRE DE CURSO", "NOTA", "CRÉDITO"]
            column_widths = [60, 80, 250, 50, 50]  # Ajuste de anchos de columna
            x_offset = 50
            c.setFont("Helvetica-Bold", 10)

            for i, header in enumerate(headers):
                c.drawString(x_offset, y, header)
                x_offset += column_widths[i]

            y -= 20  # Espacio después del encabezado
            c.line(50, y, width - 50, y)  # Línea separadora
            y -= 20

            # Dibujar datos de los cursos
            c.setFont("Helvetica", 10)
            total_credits = 0
            for course in courses:
                x_offset = 50
                c.drawString(x_offset, y, course['NIVEL'])
                x_offset += column_widths[0]
                c.drawString(x_offset, y, course['CURSO_PLAN'])
                x_offset += column_widths[1]
                c.drawString(x_offset, y, course['NOMBRE_DE_CURSO'])
                x_offset += column_widths[2]
                c.drawString(x_offset, y, course['NOTA'])
                x_offset += column_widths[3]
                c.drawString(x_offset, y, course['CREDITO'])
                total_credits += float(course['CREDITO'])
                y -= 15

                # Verificar si necesita una nueva página
                if y < 100:
                    c.drawCentredString(width / 2, 30, f"Página {page_number}")
                    c.showPage()
                    page_number += 1
                    y = height - 140
                    c.setFont("Helvetica-Bold", 12)
                    c.drawString(50, y, f"PERIODO ACADÉMICO: {period} (cont.)")
                    y -= 30
                    c.line(50, y, width - 50, y)  # Línea separadora
                    y -= 20

            # Línea separadora después de los cursos
            c.line(50, y, width - 50, y)
            y -= 20

            # Total de créditos
            c.setFont("Helvetica-Bold", 10)
            c.drawString(width - 200, y, f"TOTAL CRÉDITOS: {total_credits}")
            y -= 30

        # Pie de página
        c.setFont("Helvetica", 9)
        c.drawCentredString(width / 2, 30, "Av. Honorio Delgado 430, Urbanización Ingeniería, San Martín de Porres")
        c.drawCentredString(width / 2, 15, "http://www.upch.edu.pe")
        c.drawCentredString(width / 2, 50, f"Página {page_number}")

        # Guardar el PDF
        c.save()
        print(f"PDF generado correctamente: {filename}")

    except Exception as e:
        print(f"Error al generar el PDF: {e}")
