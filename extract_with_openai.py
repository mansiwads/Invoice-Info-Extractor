import pytesseract
import cv2
import numpy as np
import pdf2image
import os
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Get API key from environment variable
openai.api_key = os.getenv('OPENAI_API_KEY')

def extract_info_with_openai(text):
    prompt = f"""
Extract the following information from this invoice text and respond in this exact format:
invoice_number: [just the number]
bill_to: [name of person or company being billed]
total_amount: [include currency symbol]

Invoice text:
{text}
"""

    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an assistant that extracts specific information from invoice documents."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=500
    )
    
    content = response.choices[0].message.content
    
    # Simple parsing of the response
    lines = content.strip().split('\n')
    result = {}
    
    for line in lines:
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip()
            result[key] = value
    
    return result


def extract_info_from_pdf(pdf_path):
    pages = pdf2image.convert_from_path(pdf_path)
    image = np.array(pages[0])
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    threshold = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    text = pytesseract.image_to_string(threshold)
    
    info = extract_info_with_openai(text)
    
    return [
        os.path.basename(pdf_path),
        info.get('invoice_number', 'Not found'),
        info.get('bill_to', 'Not found'),
        info.get('total_amount', 'Not found')
    ]

if __name__ == "__main__":
    pdf_files = [f for f in os.listdir('.') if f.endswith('.pdf')]
    
    print("\nPDF Name | Invoice Number | Billed To | Total Amount")
    print("-" * 80)
    
    for pdf_file in pdf_files:
        result = extract_info_from_pdf(pdf_file)
        print(f"{result[0]} | {result[1]} | {result[2]} | {result[3]}") 