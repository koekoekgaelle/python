from langchain_text_splitters import RecursiveCharacterTextSplitter


def create_chunks(text: str) -> list[str]:
    """
    Verdeel een lange tekst in kleinere overlappende stukken.
    """

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
    )

    return splitter.split_text(text)