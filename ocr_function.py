# import easyocr
# from pdf2image import convert_from_path
# import numpy as np
# from PIL import Image
# import fitz  # PyMuPDF

# def extract_text_with_easyocr(file_path, languages=['en', 'hi']):
#     """
#     Extracts text from a legal document (image or PDF) in Hindi and English using EasyOCR.
    
#     Parameters:
#         file_path (str): Path to the input image or PDF file.
#         languages (list): List of language codes for OCR (default is ['en', 'hi']).
    
#     Returns:
#         str: Extracted text.
#     """
#     # Initialize EasyOCR reader
#     reader = easyocr.Reader(languages)
#     extracted_text = ""

#     # Helper function to convert PDF to images using PyMuPDF
#     def convert_pdf_to_images_with_fitz(file_path):
#         images = []
#         pdf_document = fitz.open(file_path)
#         for page_num in range(len(pdf_document)):
#             page = pdf_document[page_num]
#             pix = page.get_pixmap()
#             image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
#             images.append(image)
#         pdf_document.close()
#         return images

#     # Determine if the file is a PDF or an image
#     if file_path.lower().endswith('.pdf'):
#         try:
#             # Attempt conversion with pdf2image
#             images = convert_from_path(file_path)
#         except Exception as e:
#             print(f"Error using pdf2image: {e}. Falling back to PyMuPDF...")
#             images = convert_pdf_to_images_with_fitz(file_path)

#         for page_num, image in enumerate(images):
#             print(f"Processing page {page_num + 1}...")
#             # Convert image to NumPy array for EasyOCR
#             extracted_text += " ".join(reader.readtext(np.array(image), detail=0))  # detail=0 returns text only
#             extracted_text += "\n"
#     else:
#         # Assume the file is an image
#         image = Image.open(file_path)
#         image_np = np.array(image)  # Convert to NumPy array
#         extracted_text = " ".join(reader.readtext(image_np, detail=0))  # detail=0 returns text only

#     return extracted_text.strip()  # Clean and return the text
import os
import io
from PIL import Image
import pytesseract
from flask import jsonify
# import response
from docx import Document
import fitz  # PyMuPDF for PDF processing


def perform_ocr(file_path, filename):
    """
    Perform OCR on an uploaded file based on its type (image, PDF, DOCX).
    
    Args:
        file_path (str): The full path of the uploaded file.
        filename (str): The name of the uploaded file.
        
    Returns:
        dict: A dictionary containing the extracted text or an error message.
    """
    extracted_text = ""

    try:
        # Handle images
        if filename.lower().endswith((".jpg", ".jpeg", ".png")):
            image = Image.open(file_path)
            extracted_text = pytesseract.image_to_string(image, lang="eng+hin")

        # Handle PDFs
        elif filename.lower().endswith(".pdf"):
            with fitz.open(file_path) as doc:
                for page_num in range(doc.page_count):
                    page = doc.load_page(page_num)
                    extracted_text += page.get_text() + "\n"

                    # Extract and process images embedded in PDF
                    image_list = page.get_images(full=True)
                    for img_index, img in enumerate(image_list):
                        xref = img[0]
                        base_image = doc.extract_image(xref)
                        image_bytes = base_image["image"]

                        try:
                            image = Image.open(io.BytesIO(image_bytes))
                            if image.mode != "RGB":
                                image = image.convert("RGB")
                            extracted_text += pytesseract.image_to_string(image, lang="eng+hin") + "\n"
                        except Exception as e:
                            print(f"Error processing image on page {page_num}, image index {img_index}: {e}")
                            continue

        # Handle DOCX files
        elif filename.lower().endswith(".docx"):
            doc = Document(file_path)
            for paragraph in doc.paragraphs:
                extracted_text += paragraph.text + "\n"

        # DEBUG: Log the extracted text
        print("Extracted Text from perform_ocr:", extracted_text)

        # Return a dictionary directly
        return {"extracted_text": extracted_text.strip()}


    except Exception as e:
        print("Error occurred:", e)
        # Return a Response object for error
        return {"error": str(e)}

    finally:
        # Clean up the file after processing
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except PermissionError:
                print(f"File {file_path} is still in use. Could not delete.")

