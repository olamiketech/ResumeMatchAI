import PyPDF2
import streamlit as st

def extract_text_from_pdf(pdf_path):
    """
    Extract text from a PDF file
    
    Args:
        pdf_path (str): Path to the PDF file
        
    Returns:
        str: Extracted text from the PDF
    """
    try:
        text = ""
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            # Extract text from all pages
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text()
        
        return text.strip()
        
    except Exception as e:
        st.error(f"Error extracting text from PDF: {str(e)}")
        return ""

def validate_pdf(pdf_path):
    """
    Validate if the PDF file is readable
    
    Args:
        pdf_path (str): Path to the PDF file
        
    Returns:
        bool: True if PDF is valid, False otherwise
    """
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            # Try to access the first page
            if len(pdf_reader.pages) > 0:
                pdf_reader.pages[0].extract_text()
                return True
        return False
    except:
        return False
