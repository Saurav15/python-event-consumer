"""
analyzer.py
Provides PDF extraction and summarization utilities.
"""
import PyPDF2
import os
import google.generativeai as genai

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file at the given path using PyPDF2."""
    try:
        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            text = ''
            for page in reader.pages:
                text += page.extract_text() or ''
        return text
    except Exception as e:
        print(f"Failed to extract text from PDF: {e}")
        raise

def summarize_text_with_gemini(text):
    """Summarize the given text using Gemini (Google Generative AI). Tries multiple models if needed."""
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set!")
    genai.configure(api_key=api_key)
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(f"Summarize the following text:\n{text}")
        summary = response.text.strip()
        return summary
    except Exception as e:
        print(f"Failed to summarize text with Gemini: {e}")
        raise 