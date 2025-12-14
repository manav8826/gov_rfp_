import fitz  # PyMuPDF
from typing import List, Dict

class PDFProcessor:
    @staticmethod
    def extract_text_from_bytes(file_content: bytes) -> str:
        """
        Extracts raw text from PDF bytes.
        """
        doc = fitz.open(stream=file_content, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        return text

    @staticmethod
    def extract_structured_data(file_content: bytes) -> Dict:
        """
        Try to identify tables or specific sections.
        For MVP, we just return full text and metadata.
        """
        doc = fitz.open(stream=file_content, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
            
        return {
            "full_text": text,
            "page_count": len(doc),
            "metadata": doc.metadata
        }
