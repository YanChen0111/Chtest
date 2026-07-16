from __future__ import annotations

import io
import os
from dataclasses import dataclass
from pathlib import Path

import pytesseract
from openpyxl import load_workbook
from PIL import Image
from pypdf import PdfReader


def configure_tesseract() -> None:
    configured = os.getenv("CHTEST_TESSERACT_CMD")
    default_path = Path("D:/tools/tesseract/tesseract.exe")
    command = Path(configured) if configured else default_path
    if command.exists():
        pytesseract.pytesseract.tesseract_cmd = str(command)


configure_tesseract()


class DocumentExtractionError(Exception):
    pass


class DocumentExtractorUnavailableError(DocumentExtractionError):
    pass


@dataclass(frozen=True)
class ExtractedDocument:
    text: str
    parser_name: str
    parser_version: str
    unit_count: int
    metadata: dict[str, object]


def extract_document_text(
    *,
    artifact_type: str,
    content: bytes,
    ocr_language: str = "eng+chi_sim",
) -> ExtractedDocument:
    if artifact_type == "context_pdf":
        return extract_pdf(content)
    if artifact_type == "context_xlsx":
        return extract_xlsx(content)
    if artifact_type == "context_image":
        return extract_image_ocr(content, language=ocr_language)
    raise DocumentExtractionError("Unsupported document artifact type.")


def extract_pdf(content: bytes) -> ExtractedDocument:
    try:
        reader = PdfReader(io.BytesIO(content))
        pages = []
        for index, page in enumerate(reader.pages, start=1):
            page_text = (page.extract_text() or "").strip()
            if page_text:
                pages.append(f"# Page {index}\n\n{page_text}")
    except Exception as exc:
        raise DocumentExtractionError("PDF content could not be parsed.") from exc
    text = "\n\n".join(pages).strip()
    if not text:
        raise DocumentExtractionError("PDF contains no extractable text. Use image OCR for scanned pages.")
    return ExtractedDocument(
        text=text,
        parser_name="pypdf",
        parser_version="v1",
        unit_count=len(reader.pages),
        metadata={"page_count": len(reader.pages)},
    )


def extract_xlsx(content: bytes) -> ExtractedDocument:
    try:
        workbook = load_workbook(io.BytesIO(content), read_only=True, data_only=True)
        sections: list[str] = []
        row_count = 0
        for worksheet in workbook.worksheets:
            rows: list[str] = []
            for row_index, values in enumerate(worksheet.iter_rows(values_only=True), start=1):
                normalized = ["" if value is None else str(value) for value in values]
                if not any(normalized):
                    continue
                rows.append(f"{row_index}\t" + "\t".join(normalized))
                row_count += 1
            if rows:
                sections.append(f"# Sheet: {worksheet.title}\n\n" + "\n".join(rows))
        workbook.close()
    except Exception as exc:
        raise DocumentExtractionError("XLSX content could not be parsed.") from exc
    text = "\n\n".join(sections).strip()
    if not text:
        raise DocumentExtractionError("XLSX contains no non-empty cells.")
    return ExtractedDocument(
        text=text,
        parser_name="openpyxl",
        parser_version="v1",
        unit_count=row_count,
        metadata={"sheet_count": len(sections), "row_count": row_count},
    )


def extract_image_ocr(content: bytes, *, language: str) -> ExtractedDocument:
    try:
        with Image.open(io.BytesIO(content)) as image:
            image.load()
            width, height = image.size
            text = pytesseract.image_to_string(image, lang=language).strip()
    except pytesseract.TesseractNotFoundError as exc:
        raise DocumentExtractorUnavailableError(
            "Tesseract OCR is not installed or is not available on PATH."
        ) from exc
    except pytesseract.TesseractError as exc:
        raise DocumentExtractionError("Tesseract OCR failed to process the image.") from exc
    except Exception as exc:
        raise DocumentExtractionError("Image content could not be parsed.") from exc
    if not text:
        raise DocumentExtractionError("OCR produced no text for the image.")
    return ExtractedDocument(
        text=f"# OCR Image\n\n{text}",
        parser_name="tesseract",
        parser_version="v1",
        unit_count=1,
        metadata={"ocr_language": language, "width": width, "height": height},
    )
