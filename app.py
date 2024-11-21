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



# Load environment variables
load_dotenv()
EMAIL = os.environ["EMAIL"]
PASSWORD = os.environ["PASSWORD"]
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Set a strong secret key
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Update path as needed

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Mail configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = EMAIL
app.config['MAIL_PASSWORD'] = PASSWORD
mail = Mail(app)

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

# Create database tables
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json(force=True)
        email = data.get('email')
        password = data.get('password')
        user = User.query.filter_by(email=email).first()
        
        if user and user.password == password:
            session['user'] = email
            return jsonify({"status": "success", "user": {"email": email}})
        else:
            return redirect(url_for('login'))

    return render_template('index.html')

@app.route('/upload')
def upload():
    if 'user' in session:
        return render_template('upload.html')
    else:
        flash("Please log in first.", "error")
        return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            flash('Email and password are required.', 'error')
            return redirect(url_for('signup'))

        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'error')
            return redirect(url_for('signup'))

        new_user = User(email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()

        if user:
            new_password = generate_random_password()
            user.password = new_password
            db.session.commit()
            
            try:
                msg = Message('Your New Password', sender=app.config['MAIL_USERNAME'], recipients=[email])
                msg.body = f'Your new password is: {new_password}'
                mail.send(msg)
                flash('A new password has been sent to your email.', 'success')
            except Exception as e:
                print("Error sending email:", e)
                flash('There was an error sending the email. Please try again.', 'error')

            return redirect(url_for('forgot_password'))
        else:
            flash('Email not found.', 'error')

    return render_template('forget.html')


# UPLOAD_FOLDER = ('uploads')
# ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'pdf', 'docx'}# Limit file size to 16 MB

# app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  

def preprocess_image(image):
    # Convert image to grayscale
    image = image.convert("L")
    
    # Apply thresholding to enhance text contrast
    image = image.point(lambda p: p > 180 and 255)
    
    # Apply sharpening filter
    image = image.filter(ImageFilter.SHARPEN)

    return image

# Configure the upload folder
UPLOAD_FOLDER = './uploaded_files'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create the upload folder if it doesn't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# @app.route('/perform_ocr/', methods=['POST'])
# def perform_ocr():
#     global uploaded_file_path  # Use a global variable to store the file path

#     if 'file' not in request.files:
#         return jsonify({"error": "No file part in the request"}), 400

#     file = request.files['file']

#     if file.filename == '':
#         return jsonify({"error": "No selected file"}), 400

#     # Save the file securely
#     filename = secure_filename(file.filename)
#     uploaded_file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#     os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
#     file.save(uploaded_file_path)

#     # Replace '\' with '\\' in the full file path
#     uploaded_file_path = uploaded_file_path.replace("\\", "\\\\")

#     # Perform OCR on the saved file
#     extracted_text = ocr_function.extract_text_with_easyocr(uploaded_file_path)

#     if not extracted_text:
#         return jsonify({"error": "No text was extracted from the document."}), 500

#     return jsonify({"extracted_text": extracted_text})



@app.route("/perform_ocr", methods=["POST"])
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

        # Extract filename from the file path
        filename = os.path.basename(uploaded_file_path)

        # Perform OCR on the saved file
        ocr_result = ocr_function.perform_ocr(uploaded_file_path, filename)

        # Validate OCR result
        if not ocr_result or "extracted_text" not in ocr_result:
            return jsonify({"error": "No text was extracted from the document."}), 500

        # Return the extracted text
        return jsonify(ocr_result)

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
    # try:
    #     filename = secure_filename(file.filename)
    #     file_path = os.path.join("UPLOAD_FOLDER", filename)
    #     file.save(file_path)

    #     extracted_text = ""

    #     # Handle images
    #     if filename.lower().endswith((".jpg", ".jpeg", ".png")):
    #         image = Image.open(file_path)
    #         extracted_text = pytesseract.image_to_string(image, lang="eng+hin")

    #     # Handle PDFs
    #     elif filename.lower().endswith(".pdf"):
    #         with fitz.open(file_path) as doc:
    #             for page_num in range(doc.page_count):
    #                 page = doc.load_page(page_num)
    #                 extracted_text += page.get_text() + "\n"

    #                 image_list = page.get_images(full=True)
    #                 for img_index, img in enumerate(image_list):
    #                     xref = img[0]
    #                     base_image = doc.extract_image(xref)
    #                     image_bytes = base_image["image"]

    #                     try:
    #                         image = Image.open(io.BytesIO(image_bytes))
    #                         if image.mode != "RGB":
    #                             image = image.convert("RGB")

    #                         extracted_text += pytesseract.image_to_string(image, lang="eng+hin") + "\n"
    #                     except Exception as e:
    #                         print(f"Error processing image on page {page_num}, image index {img_index}: {e}")
    #                         continue

    #     # Handle DOCX files
    #     elif filename.lower().endswith(".docx"):
    #         doc = Document(file_path)
    #         for paragraph in doc.paragraphs:
    #             extracted_text += paragraph.text + "\n"

    #     # DEBUG: Log the extracted text
    #     print("Extracted Text from perform_ocr:", extracted_text)

    #     # Return a dictionary directly
    #     return {"extracted_text": extracted_text}

    # except Exception as e:
    #     print("Error occurred:", e)
    #     # Return a Response object for error
    #     return jsonify({"error": str(e)}), 500


    # if os.path.exists(file_path):
    #         try:
    #             os.remove(file_path)
    #         except PermissionError:
    #             print(f"File {file_path} is still in use. Could not delete.")


# @app.route("/perform_ocr", methods=["POST"])
# def perform_ocr():
#     if "file" not in request.files:
#         return jsonify({"error": "No file part"}), 400

#     file = request.files["file"]
#     if file.filename == "":
#         return jsonify({"error": "No selected file"}), 400

#     try:
#         filename = secure_filename(file.filename)
#         file_path = os.path.join("uploads", filename)
#         file.save(file_path)

#         extracted_text = ""

#         if filename.lower().endswith((".jpg", ".jpeg", ".png")):
#             image = Image.open(file_path)
#             extracted_text = pytesseract.image_to_string(image, lang="eng+hin")

#         elif filename.lower().endswith(".pdf"):
#             with fitz.open(file_path) as doc:
#                 for page_num in range(doc.page_count):
#                     page = doc.load_page(page_num)
#                     extracted_text += page.get_text() + "\n"

#                     image_list = page.get_images(full=True)
#                     for img_index, img in enumerate(image_list):
#                         xref = img[0]
#                         base_image = doc.extract_image(xref)
#                         image_bytes = base_image["image"]

#                         try:
#                             image = Image.open(io.BytesIO(image_bytes))
#                             processed_image = preprocess_image(image)
#                             if image.mode != "RGB":
#                                 image = image.convert("RGB")

#                             extracted_text += pytesseract.image_to_string(image, lang="eng+hin") + "\n"
#                         except Exception as e:
#                             print(f"Error processing image on page {page_num}, image index {img_index}: {e}")
#                             continue

#         elif filename.lower().endswith(".docx"):
#             doc = Document(file_path)
#             for paragraph in doc.paragraphs:
#                 extracted_text += paragraph.text + "\n"
#   # DEBUG: Log the extracted text
#         print("Extracted Text from perform_ocr:", extracted_text)
#         # Return as a dictionary instead of a tuple
#         # return jsonify({"extracted_text": extracted_text})
#         return {"extracted_text": extracted_text}

#     except Exception as e:
#         print("Error occurred:", e)
#         return jsonify({"error": str(e)}), 500

#     finally:
#         if os.path.exists(file_path):
#             try:
#                 os.remove(file_path)
#             except PermissionError:
#                 print(f"File {file_path} is still in use. Could not delete.")


# @app.route('/extract-entities', methods=['GET', 'POST'])
# def extract_entities():
#     try:
#         # Call the perform_ocr function
#         ocr_response = perform_ocr()

#         # DEBUG: Log the response
#         print("OCR Response:", ocr_response)

#         # Check the response format
#         if isinstance(ocr_response, dict):
#             ocr_data = ocr_response  # Use it as a dictionary
#         elif isinstance(ocr_response, Response):
#             ocr_data = ocr_response.get_json()  # Extract JSON from the Response object
#         else:
#             return jsonify({"error": "Unexpected OCR response format"}), 500

#         # Extract the text from the OCR response
#         extracted_text = ocr_data.get("extracted_text", "")

#         if not extracted_text:
#             return jsonify({"error": "No text extracted"}), 400

#         print("Extracted Text:", extracted_text)  # Debugging

#         # Use the `extract_entities_from_text` function from test.py
#         entities_response = test.extract_entities_from_text(extracted_text)

#         # Extract entities from the response text
#         entities = entities_response.strip()  # Assuming response is a string with entities

#         # Render the entities to the result.html page
#         return render_template('result.html', entities=entities)

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# Initialize the global variable
uploaded_file_path = None

@app.route('/perform_entity_recognition', methods=['POST'])
def perform_entity_recognition():
    try:
        global uploaded_file_path

        # Check if file path is set
        if not uploaded_file_path:
            return jsonify({"error": "No file path available. Perform OCR first."}), 400

        # Perform OCR and entity extraction
        extracted_text = ocr_function.perform_ocr(uploaded_file_path)
        if not extracted_text or "extracted_text" not in extracted_text:
            return jsonify({"error": "No text was extracted from the document."}), 500

        text_for_entity_recognition = extracted_text.get("extracted_text", "")
        entities = entity_recognition.extract_entities_from_text(text_for_entity_recognition, GEMINI_API_KEY)

        if not entities:
            return jsonify({"error": "No entities were recognized in the text."}), 500

        return jsonify({"extracted_entities": entities})

    except Exception as e:
        print(f"Error during entity recognition: {e}")
        return jsonify({"error": str(e)}), 500

        # # Return the extracted entities as JSON
        # return jsonify({"extracted_entities": entities})
        
   

# @app.route("/extract_entities", methods=["POST"])
# def extract_entities():
#     try:
#         # Check if JSON payload exists
#         if not request.is_json:
#             return jsonify({"error": "Invalid content type. Must be application/json."}), 400

#         # Parse JSON data
#         data = request.get_json()
#         filename = data.get("filename")
#         file_content = data.get("file_content")

#         # Validate the payload
#         if not filename or not file_content:
#             return jsonify({"error": "Filename or file content is missing."}), 400

#         # Decode the Base64 content and save it as a temporary file
#         decoded_file = base64.b64decode(file_content)
#         uploaded_file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
#         os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
#         with open(uploaded_file_path, "wb") as f:
#             f.write(decoded_file)

#         # Extract entities directly from the file
#         entities_result = extract_entities_from_file(uploaded_file_path, filename)

#         # Clean up the uploaded file
#         os.remove(uploaded_file_path)

#         return jsonify(entities_result)

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# @app.route('/extract-entities', methods=['GET', 'POST'])
# def extract_entities():
#     print("Request JSON:", request.get_json()) 
#     try:
#         # Call the perform_ocr function
#         ocr_response = perform_ocr()

#         # DEBUG: Log the OCR response
#         print("OCR Response:", ocr_response)

#         # If ocr_response is a tuple, unpack it
#         if isinstance(ocr_response, tuple):
#             response_data, status_code = ocr_response
#             if status_code != 200:  # If there's an error, propagate it
#                 return response_data

#         # Ensure ocr_response is a dictionary
#         if isinstance(ocr_response, dict):
#             data = ocr_response
#         else:
#             return jsonify({"error": "Unexpected OCR response format"}), 500

#         # # Extract the text from the OCR response
#         # extracted_text = ocr_data.get("extracted_text", "")

#         # if not extracted_text:
#         #     return jsonify({"error": "No text extracted"}), 400
        
#         # Parse the JSON data  
#         # ocr_data = response_data.get_json()
    
#         # # Extract the text from the OCR response
#         # extracted_text = ocr_data.get("extracted_text", "")
#         # if not extracted_text:
#         #     return jsonify({"error": "No text extracted"}), 400
#             # Validate and parse JSON input
#         data = request.get_json()
#         if not data or "text" not in data:
#             return jsonify({"error": "Invalid input. 'text' field is required."}), 400

#         # Extract entities from the provided text
#         extracted_text = data["text"].strip()
#         if not extracted_text:
#             return jsonify({"error": "Text field cannot be empty."}), 400

#         # print("Extracted Text:", extracted_text)  # Debugging

#         # Use the `extract_entities_from_text` function from test.py
#         entities_response = test.extract_entities_from_text(extracted_text)

#         # Extract entities from the response text
#         entities = entities_response.strip()  # Assuming response is a string with entities

#         # Render the entities to the result.html page
#         return render_template('result.html', entities=entities)

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# Display Extracted Entities (This can directly render from the extract_entities function)

@app.route('/display-entities', methods=['GET'])
def display_entities():
    entities = request.args.get("entities", "")
    return render_template('result.html', entities=entities)


if __name__ == "__main__":
    app.run(debug=True)
