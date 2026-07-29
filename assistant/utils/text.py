import re
import unicodedata


def create_slug(text: str) -> str:
    """
    Zet een titel om naar een URL-vriendelijke slug.
    """

    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.lower()

    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-+", "-", text)

    return text.strip("-")