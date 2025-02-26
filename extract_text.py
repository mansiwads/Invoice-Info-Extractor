import pytesseract
import cv2
import numpy as np
import pdf2image
import os
import re

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_values(text):
    invoice_pattern = r'Invoice\s*(?:No\.?|Number|#)?\s*:?\s*(\d+)'
    bill_to_pattern = r'Bill\s*To\s*:?\s*(.*?)(?=\n\n|\n[A-Z]|$)'
    total_pattern = r'Total\s*:?\s*\$?\s*([\d,]+\.?\d{0,2})'
    
    invoice_match = re.search(invoice_pattern, text, re.IGNORECASE)
    bill_to_match = re.search(bill_to_pattern, text, re.IGNORECASE | re.DOTALL)
    total_match = re.search(total_pattern, text, re.IGNORECASE)
    
    return {
        'invoice_number': invoice_match.group(1) if invoice_match else 'Not found',
        'bill_to': bill_to_match.group(1).strip() if bill_to_match else 'Not found',
        'total_amount': f"${total_match.group(1)}" if total_match else 'Not found'
    }



def extract_info_from_pdf(pdf_path):
    pages = pdf2image.convert_from_path(pdf_path)
    image = np.array(pages[0])
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    threshold = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    text = pytesseract.image_to_string(threshold)
    
    info = extract_values(text)
    
    return [
        os.path.basename(pdf_path),
        info['invoice_number'],
        info['bill_to'],
        info['total_amount']
    ]


if __name__ == "__main__":
    pdf_files = [f for f in os.listdir('.') if f.endswith('.pdf')]
    
    print("\nPDF Name | Invoice Number | Billed To | Total Amount")
    print("-" * 80)
    
    for pdf_file in pdf_files:
        result = extract_info_from_pdf(pdf_file)
        print(f"{result[0]} | {result[1]} | {result[2]} | {result[3]}") 