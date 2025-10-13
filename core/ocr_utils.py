import pytesseract
from PIL import Image
import logging

logger = logging.getLogger(__name__)

def extract_text_from_image(image_path):
    """
    Extract text from an image file using pytesseract OCR.
    Args:
        image_path (str): Path to the image file.
    Returns:
        str: Extracted text from the image.
    """
    try:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img)
        return text
    except Exception as e:
        logger.error(f"Failed to extract text from image {image_path}: {e}")
        return ""
