# import google.generativeai as genai

# # Replace 'your-gemini-api-key' with your actual Gemini API key
# api_key = "AIzaSyDPf-_j6vVw1i83CggXuVJQDxByJE5jssA"

# # Configure the API key
# genai.configure(api_key=api_key)

# # Create the model
# generation_config = {
#   "temperature": 0,
#   "top_p": 0.95,
#   "top_k": 64,
#   "max_output_tokens": 8192,
#   "response_mime_type": "text/plain",
# }
# safety_settings = [
#   {
#     "category": "HARM_CATEGORY_HARASSMENT",
#     "threshold": "BLOCK_NONE",
#   },
#   {
#     "category": "HARM_CATEGORY_HATE_SPEECH",
#     "threshold": "BLOCK_MEDIUM_AND_ABOVE",
#   },
#   {
#     "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
#     "threshold": "BLOCK_MEDIUM_AND_ABOVE",
#   },
#   {
#     "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
#     "threshold": "BLOCK_MEDIUM_AND_ABOVE",
#   },
# ]

# model = genai.GenerativeModel(
#   model_name="gemini-1.5-pro",
#   safety_settings=safety_settings,
#   generation_config=generation_config,
#   system_instruction="Find entities from the Hindi text among the following entities: . Just mark the entities presnt only,dont give explanation why you set that entity.give which word is which entity ",
# )

# # Start a chat session
# chat_session = model.start_chat(
#     history=[]
# )

# print("Bot: Hello, how can I help you?")
# print()

# while True:
#     user_input = input("You: ")
#     print()

#     response = chat_session.send_message(user_input)
#     model_response = response.text

#     print(f'Bot: {model_response}')
#     print()

#     chat_session.history.append({"role": "user", "parts": [user_input]})
#     chat_session.history.append({"role": "model", "parts": [model_response]})@app.route("/perform_ocr", methods=["POST"])
import base64
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, Response
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
import random
import string
from dotenv import load_dotenv
import os
import pytesseract
import io
from werkzeug.utils import secure_filename
from PIL import Image, ImageEnhance, ImageFilter
from docx import Document
import fitz  # PyMuPDF
import google.generativeai as genai
import test
import ocr_function 
import entity_recognition 

GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]
app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Set a strong secret key
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Update path as needed

# Configure the upload folder
UPLOAD_FOLDER = './uploaded_files'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create the upload folder if it doesn't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
    
def perform_ocr_endpoint():
    try:
        # Debugging information
        print("Request Method:", request.method)  # Should be POST
        print("Request Form:", request.form)      # Form data, if any
        print("Request Files:", request.files) 
        print("Content-Type:", request.content_type)  # Should show the uploaded file

        # Check if the "file" key is present
        if "file" not in request.files:
            return jsonify({"error": "No file part. Check your form or request."}), 400

        file = request.files["file"]

        # Check if a file was selected
        if file.filename == "":
            return jsonify({"error": "No selected file. Please upload a file."}), 400

        # Save the file securely
        filename = secure_filename(file.filename)
        uploaded_file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
        file.save(uploaded_file_path)

        # Perform OCR on the saved file
        ocr_result = ocr_function.perform_ocr(uploaded_file_path, filename)

        # Validate OCR result
        if not ocr_result or "extracted_text" not in ocr_result:
            return jsonify({"error": "No text was extracted from the document."}), 500

        extracted_text = ocr_result["extracted_text"]

        # Return extracted text for further processing
        return jsonify({"extracted_text": extracted_text})

    except Exception as e:
        # Log the error for debugging
        print(f"Error during OCR processing: {e}")
        return jsonify({"error": str(e)}), 500

    finally:
        # Clean up the uploaded file
        if os.path.exists(uploaded_file_path):
            try:
                os.remove(uploaded_file_path)
            except Exception as cleanup_error:
                print(f"Failed to delete {uploaded_file_path}: {cleanup_error}")



@app.route("/perform_entity_recognition", methods=["POST"])
def perform_entity_recognition():
    try:
        # Get extracted text from the request body
        request_data = request.get_json()
        if not request_data or "extracted_text" not in request_data:
            return jsonify({"error": "No extracted text provided. Perform OCR first."}), 400

        extracted_text = request_data["extracted_text"]

        # Perform entity recognition
        entities = entity_recognition.extract_entities_from_text(extracted_text, GEMINI_API_KEY)

        if not entities:
            return jsonify({"error": "No entities were recognized in the text."}), 500

        return jsonify({"extracted_entities": entities})

    except Exception as e:
        print(f"Error during entity recognition: {e}")
        return jsonify({"error": str(e)}), 500
