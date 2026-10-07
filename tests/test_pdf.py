from io import BytesIO
from pathlib import Path
import pytest
from PIL import Image as PILImage
from pypdf import PdfReader
from synapse_qr_print.pdf import build_pdf

FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

pytestmark = pytest.mark.skipif(
    not Path(FONT_PATH).exists(), reason="не установлен шрифт DejaVuSans"
)

METADATA = {
    "Отправитель": "@petr:localhost",
    "Комната": "!abc123:localhost",
    "Время": "2026-10-07 11:20:00",
}

@pytest.fixture
def qr_png():
    """Простая картинка вместо настоящего QR: тесту важен сам PDF, а не код."""
    img = PILImage.new("RGB", (100, 100), "white")
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

def read_pdf(pdf_bytes):
    """Возвращает (весь текст PDF, количество страниц)."""
    reader = PdfReader(BytesIO(pdf_bytes))
    text = "".join(page.extract_text() for page in reader.pages)
    return text, len(reader.pages)

def test_result_is_pdf(qr_png):
    pdf = build_pdf("Привет", METADATA, qr_png, FONT_PATH)
    assert pdf.startswith(b"%PDF")

def test_russian_text_and_metadata_are_readable(qr_png):
    pdf = build_pdf("Привет, это тест", METADATA, qr_png, FONT_PATH)
    text, _ = read_pdf(pdf)
    assert "Привет, это тест" in text
    assert "@petr:localhost" in text
    assert "!abc123:localhost" in text
    assert "2026-10-07 11:20:00" in text

def test_special_characters_are_kept(qr_png):
    pdf = build_pdf("a < b & c > d", METADATA, qr_png, FONT_PATH)
    text, _ = read_pdf(pdf)
    assert "a < b & c > d" in text

def test_multiline_message(qr_png):
    pdf = build_pdf("первая строка\nвторая строка", METADATA, qr_png, FONT_PATH)
    text, _ = read_pdf(pdf)
    assert "первая строка" in text
    assert "вторая строка" in text

def test_fits_on_one_page(qr_png):
    long_body = "Длинное сообщение. " * 60  # около 1100 символов, близко к пределу QR
    pdf = build_pdf(long_body, METADATA, qr_png, FONT_PATH)
    _, pages = read_pdf(pdf)
    assert pages == 1