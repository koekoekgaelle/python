
import pytesseract
from langchain_core.documents import Document
from pdf2image import convert_from_bytes


OCR_LANGUAGE_MAP = {
    "nl": "nld",
    "en": "eng",
    "de": "deu",
    "fr": "fra",
}


def load_pdf_with_ocr(
    uploaded_file,
    language: str = "nl",
) -> list[Document]:
    """
    Zet een gescande PDF om naar LangChain Document-objecten.
    """

    pdf_bytes = uploaded_file.getvalue()

    if not pdf_bytes:
        return []

    tesseract_language = OCR_LANGUAGE_MAP.get(
        language,
        "eng",
    )

    images = convert_from_bytes(
        pdf_bytes,
        dpi=300,
    )

    documents = []

    for page_number, image in enumerate(images, start=1):
        text = pytesseract.image_to_string(
            image,
            lang=tesseract_language,
            config="--oem 3 --psm 6",
        )

        if not text or not text.strip():
            continue

        documents.append(
            Document(
                page_content=text.strip(),
                metadata={
                    "source": uploaded_file.name,
                    "page": page_number,
                    "extraction_method": "ocr",
                },
            )
        )

    return documents