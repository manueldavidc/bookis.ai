import io
import requests
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.fonts import addMapping
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Try to register custom fonts, fall back to defaults if not available
try:
    pdfmetrics.registerFont(TTFont('ComicSans', 'static/fonts/ComicSans.ttf'))
    pdfmetrics.registerFont(TTFont('TimesRoman', 'static/fonts/TimesRoman.ttf'))
    addMapping('ComicSans', 0, 0, 'ComicSans')
    addMapping('TimesRoman', 0, 0, 'TimesRoman')
    print("Custom fonts registered successfully")
except Exception as e:
    print(f"Error registering custom fonts: {e}")
    print("Falling back to default fonts")
    ComicSans = 'Helvetica'
    TimesRoman = 'Times-Roman'

def generate_pdf(title, content, cover_image_url, age):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=72, bottomMargin=72)
    story = []

    # Choose font based on age
    font_name = ComicSans if 4 <= age <= 8 else TimesRoman
    font_size = 14 if 4 <= age <= 8 else 12

    # Create styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', parent=styles['Title'], fontName=font_name, fontSize=24)
    content_style = ParagraphStyle('Content', parent=styles['Normal'], fontName=font_name, fontSize=font_size, leading=font_size*1.2)

    # Add title
    story.append(Paragraph(title, title_style))
    story.append(Spacer(1, 24))

    # Add cover image
    response = requests.get(cover_image_url)
    img = Image(io.BytesIO(response.content), width=400, height=300)
    story.append(img)
    story.append(Spacer(1, 24))

    # Add content with space for illustrations
    paragraphs = content.split('\n\n')
    for i, paragraph in enumerate(paragraphs):
        story.append(Paragraph(paragraph, content_style))
        story.append(Spacer(1, 12))
        if i % 2 == 1:  # Add space for illustration every other paragraph
            story.append(Spacer(1, 200))  # Space for illustration

    doc.build(story)
    buffer.seek(0)
    return buffer

# Amazon KDP requirements
def generate_kdp_pdf(title, content, cover_image_url, age):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=(504, 720), topMargin=36, bottomMargin=36, leftMargin=36, rightMargin=36)
    # ... (rest of the function remains similar to generate_pdf, with adjusted sizes and styles)
    return buffer
