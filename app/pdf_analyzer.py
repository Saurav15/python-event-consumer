import PyPDF2
import os
import google.generativeai as genai
from .config import get_openai_api_key

def extract_text_from_pdf(pdf_path: str) -> str:
    with open(pdf_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        text = ''
        for page in reader.pages:
            text += page.extract_text() or ''
    return text

def summarize_text_with_gemini(text: str, max_bytes: int = 1000000) -> str:
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        raise ValueError('GEMINI_API_KEY not set in environment')
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash-001')
    prompt = (
        "You are an expert document summarizer. "
        "Summarize the following PDF content in clear, concise language. "
        "The summary must be less than 1MB and should capture all key points, important facts, and main ideas. "
        "Do not include any unnecessary details or formatting.\n\n"
        f"PDF Content:\n{text[:8000]}"
    )
    response = model.generate_content(prompt)
    summary = response.text.strip()
    if len(summary.encode('utf-8')) > max_bytes:
        summary = summary.encode('utf-8')[:max_bytes].decode('utf-8', errors='ignore')
    return summary 