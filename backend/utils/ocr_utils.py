import pytesseract
from PIL import Image


def image_to_text(image_path: str) -> str:
    image = Image.open(image_path)
    return pytesseract.image_to_string(image)
