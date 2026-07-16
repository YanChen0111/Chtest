from __future__ import annotations

import io

from openpyxl import Workbook
from PIL import Image

from backend.app.modules.ai_runtime import document_extraction as extraction


def test_extract_pdf_preserves_page_boundaries(monkeypatch) -> None:
    class FakePage:
        def __init__(self, text: str) -> None:
            self.text = text

        def extract_text(self) -> str:
            return self.text

    class FakeReader:
        def __init__(self, _stream) -> None:
            self.pages = [FakePage("first page"), FakePage("second page")]

    monkeypatch.setattr(extraction, "PdfReader", FakeReader)

    result = extraction.extract_pdf(b"pdf")

    assert result.parser_name == "pypdf"
    assert result.unit_count == 2
    assert "# Page 1" in result.text
    assert "# Page 2" in result.text


def test_extract_xlsx_preserves_sheet_and_row_locations() -> None:
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Limits"
    sheet.append(["Current", "Fallback"])
    sheet.append([32, "offline"])
    payload = io.BytesIO()
    workbook.save(payload)

    result = extraction.extract_xlsx(payload.getvalue())

    assert result.parser_name == "openpyxl"
    assert result.unit_count == 2
    assert "# Sheet: Limits" in result.text
    assert "1\tCurrent\tFallback" in result.text
    assert "2\t32\toffline" in result.text


def test_extract_image_ocr_records_engine_metadata(monkeypatch) -> None:
    image_payload = io.BytesIO()
    Image.new("RGB", (20, 10), "white").save(image_payload, format="PNG")
    monkeypatch.setattr(extraction.pytesseract, "image_to_string", lambda _image, lang: "32A limit")

    result = extraction.extract_image_ocr(image_payload.getvalue(), language="eng")

    assert result.parser_name == "tesseract"
    assert result.metadata == {"ocr_language": "eng", "width": 20, "height": 10}
    assert "32A limit" in result.text
