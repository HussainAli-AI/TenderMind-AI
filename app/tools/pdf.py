try:
    import pypdfium2 as pdfium
    HAS_PYPDFIUM2 = True
except ImportError:
    pdfium = None
    HAS_PYPDFIUM2 = False

from dataclasses import dataclass
from typing import List
from io import BytesIO

MIN_CHARS_FOR_DIGITAL = 100

@dataclass
class PageData:
    page_num: int
    text: str
    method: str  # "text" or "ocr"

def extract_pdf_pages(file_bytes: bytes) -> List[PageData]:
    """
    Extracts text from each PDF page using pypdfium2 with optional pytesseract OCR fallback,
    or falls back to pypdf if pypdfium2 is unavailable.
    """
    pages: List[PageData] = []
    
    if HAS_PYPDFIUM2 and pdfium is not None:
        pdf = pdfium.PdfDocument(file_bytes)
        for idx in range(len(pdf)):
            page = pdf[idx]
            textpage = page.get_textpage()
            text = textpage.get_text_range().strip()
            
            if len(text) >= MIN_CHARS_FOR_DIGITAL:
                pages.append(PageData(page_num=idx + 1, text=text, method="text"))
            else:
                try:
                    import pytesseract
                    pil_image = page.render(scale=2.0).to_pil()
                    ocr_text = pytesseract.image_to_string(pil_image, lang="eng")
                    clean_ocr = ocr_text.strip()
                    if len(clean_ocr) > len(text):
                        pages.append(PageData(page_num=idx + 1, text=clean_ocr, method="ocr"))
                    else:
                        pages.append(PageData(page_num=idx + 1, text=text, method="text"))
                except Exception:
                    pages.append(PageData(page_num=idx + 1, text=text if text else "[Scanned Page / Low Text Density]", method="text"))
        return pages

    # Fallback to pypdf
    try:
        import pypdf
        reader = pypdf.PdfReader(BytesIO(file_bytes))
        for idx, page in enumerate(reader.pages):
            text = (page.extract_text() or "").strip()
            pages.append(PageData(page_num=idx + 1, text=text if text else "[Page text empty]", method="text"))
    except Exception as e:
        pages.append(PageData(page_num=1, text=f"Error reading PDF: {e}", method="error"))
        
    return pages
