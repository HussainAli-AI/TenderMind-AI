import pypdfium2 as pdfium
from dataclasses import dataclass
from typing import List

MIN_CHARS_FOR_DIGITAL = 100

@dataclass
class PageData:
    page_num: int
    text: str
    method: str  # "text" or "ocr"

def extract_pdf_pages(file_bytes: bytes) -> List[PageData]:
    """
    Extracts text from each PDF page using pypdfium2 with optional pytesseract OCR fallback.
    """
    pdf = pdfium.PdfDocument(file_bytes)
    pages: List[PageData] = []
    
    for idx in range(len(pdf)):
        page = pdf[idx]
        textpage = page.get_textpage()
        text = textpage.get_text_range().strip()
        
        if len(text) >= MIN_CHARS_FOR_DIGITAL:
            pages.append(PageData(page_num=idx + 1, text=text, method="text"))
        else:
            # Attempt OCR fallback
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
                # Fallback to whatever text was extracted
                pages.append(PageData(page_num=idx + 1, text=text if text else "[Scanned Page / Low Text Density]", method="text"))
                
    return pages
