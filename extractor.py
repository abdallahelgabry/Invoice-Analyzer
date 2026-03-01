import fitz
import pytesseract
from PIL import Image
import io


def extract_text_from_pdf(file_bytes: bytes) -> str:
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text.strip()


def extract_text_from_image(file_bytes: bytes) -> str:
    image = Image.open(io.BytesIO(file_bytes))
    text = pytesseract.image_to_string(image, lang="eng+ara")
    return text.strip()


def extract_text(file_bytes: bytes, file_type: str) -> str:
    if file_type == "application/pdf":
        return extract_text_from_pdf(file_bytes)
    else:
        return extract_text_from_image(file_bytes)