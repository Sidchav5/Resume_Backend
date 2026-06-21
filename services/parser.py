"""
Resume text extraction service.
Supports PDF (via pdfplumber + PyPDF2 fallback) and DOCX (via python-docx).
"""
import io
import re
import pdfplumber
from PyPDF2 import PdfReader
from docx import Document


def extract_text_from_pdf(file_bytes):
    """Extract text from PDF using pdfplumber, with PyPDF2 fallback."""
    text = ""
    
    # Primary: pdfplumber (better layout preservation)
    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception:
        text = ""
    
    # Fallback: PyPDF2
    if not text.strip():
        try:
            reader = PdfReader(io.BytesIO(file_bytes))
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        except Exception:
            text = ""
    
    return text.strip()


def extract_text_from_docx(file_bytes):
    """Extract text from DOCX file."""
    try:
        doc = Document(io.BytesIO(file_bytes))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        return "\n".join(paragraphs)
    except Exception:
        return ""


def extract_text(file_bytes, filename):
    """Route to correct extractor based on file extension."""
    ext = filename.rsplit('.', 1)[-1].lower()
    if ext == 'pdf':
        return extract_text_from_pdf(file_bytes)
    elif ext == 'docx':
        return extract_text_from_docx(file_bytes)
    else:
        raise ValueError(f"Unsupported file type: {ext}")


# Section heading patterns for detection
SECTION_PATTERNS = {
    'contact': r'(?i)(contact\s*(info|information|details)?|personal\s*(info|information|details)?|email|phone|address)',
    'summary': r'(?i)(summary|objective|profile|about\s*me|professional\s*summary|career\s*objective)',
    'education': r'(?i)(education|academic|qualification|degree)',
    'experience': r'(?i)(experience|work\s*history|employment|professional\s*experience|work\s*experience)',
    'projects': r'(?i)(project|personal\s*project|academic\s*project)',
    'skills': r'(?i)(skill|technical\s*skill|competenc|proficienc|technologies)',
    'certifications': r'(?i)(certification|certificate|credential|license)',
    'achievements': r'(?i)(achievement|award|honor|accomplishment)',
}


def detect_sections(text):
    """Detect which resume sections are present in the text."""
    found = {}
    for section, pattern in SECTION_PATTERNS.items():
        match = re.search(pattern, text)
        found[section] = match is not None
    return found
