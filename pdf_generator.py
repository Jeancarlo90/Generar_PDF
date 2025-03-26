# pdf_generator.py
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def generate_pdf(data, filename):
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter

    # Set title
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2, height - 50, "FICHA DE NOTAS")

    # Set table header
    c.setFont("Helvetica-Bold", 12)
    y = height - 80
    headers = ["NIVEL", "CURSO PLAN", "CURSO OFERTA", "NOMBRE DE CURSO", "NOTA", "CREDITO"]
    for header in headers:
        c.drawString(10, y, header)
        y -= 20

    # Set table data
    c.setFont("Helvetica", 10)
    for row in data:
        y -= 20
        c.drawString(10, y, f"{row['NIVEL']}")
        c.drawString(60, y, f"{row['CURSO_PLAN']}")
        c.drawString(110, y, f"{row['CURSO_OFERTA']}")
        c.drawString(160, y, f"{row['NOMBRE_DE_CURSO']}")
        c.drawString(260, y, f"{row['NOTA']}")
        c.drawString(310, y, f"{row['CREDITO']}")

    c.save()
