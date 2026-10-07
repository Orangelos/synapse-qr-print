from io import BytesIO
from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer

FONT_NAME = "QrPrintFont"
QR_SIZE = 70 * mm

def _register_font(font_path):
    if FONT_NAME not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont(FONT_NAME, font_path))

def _to_markup(text):
    return escape(text).replace("\n", "")

def build_pdf(body, metadata, qr_png, font_path):
    _register_font(font_path)
    meta_style = ParagraphStyle(name="meta", fontName=FONT_NAME, fontSize=10, leading=13)
    body_style = ParagraphStyle(name="body", fontName=FONT_NAME, fontSize=12, leading=16)
    story = []
    for key, value in metadata.items():
        line = f"{key}: {value}"
        story.append(Paragraph(_to_markup(line), meta_style))
    story.append(Spacer(1, 6 * mm))
    story.append(Paragraph(_to_markup(body), body_style))
    story.append(Spacer(1, 10 * mm))
    story.append(Image(BytesIO(qr_png), width=QR_SIZE, height=QR_SIZE))
    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
        title="Matrix message",
    )
    doc.build(story)
    return buf.getvalue()