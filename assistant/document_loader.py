from langchain_core.documents import Document
from pypdf import PdfReader


def load_pdf(file) -> list[Document]:
    """
    Lees een PDF pagina voor pagina.

    Elke pagina wordt teruggegeven als een LangChain Document
    met de tekst en bijbehorende metadata.
    """

    reader = PdfReader(file)
    documents = []

    for page_number, page in enumerate(reader.pages, start=1):
        page_text = page.extract_text()

        if page_text:
            document = Document(
                page_content=page_text,
                metadata={
                    "source": file.name,
                    "page": page_number,
                },
            )

            documents.append(document)

    return documents