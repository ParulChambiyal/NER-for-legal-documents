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

