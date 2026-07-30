from io import BytesIO

from langchain_core.documents import Document
from pypdf import PdfReader


def load_pdf(uploaded_file) -> list[Document]:
    """
    Lees een geüploade PDF uit en maak per pagina een Document.
    """
    pdf_bytes = uploaded_file.getvalue()
    reader = PdfReader(BytesIO(pdf_bytes))

    documents = []

    for page_index, page in enumerate(reader.pages, start=1):
        text = page.extract_text()

        if not text or not text.strip():
            continue

        documents.append(
            Document(
                page_content=text,
                metadata={
                    "source": uploaded_file.name,
                    "page": page_index,
                },
            )
        )

    return documents