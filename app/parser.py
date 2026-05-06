import fitz # PyMuPDF
import logging

logger = logging.getLogger(__name__)

def extract_text_from_pdf(pdf_path):
    pages_text = []
    try:
        doc = fitz.open(pdf_path)
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text("text")
            pages_text.append({
                "page_number": page_num + 1,
                "text": text
            })
        doc.close()
    except Exception as e:
        logger.error(f"Error reading PDF {pdf_path}: {e}")
    return pages_text
