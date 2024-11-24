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

def generate_random_password(length=12):
    """
    Generate a secure random password.
    
    Parameters:
        length (int): Length of the password. Default is 12.
        
    Returns:
        str: A random password.
    """
    characters = string.ascii_letters + string.digits + string.punctuation
    # Ensure at least one character of each type
    password = (
        random.choice(string.ascii_lowercase) +
        random.choice(string.ascii_uppercase) +
        random.choice(string.digits) +
        random.choice(string.punctuation)
    )
    # Fill the rest of the password length with random choices
    password += ''.join(random.choices(characters, k=length - 4))
    # Shuffle to avoid predictable patterns
    password = ''.join(random.sample(password, len(password)))
    return password


@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
# Function to generate a random password

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
        request_data = request.get_json()
        if not request_data or "extracted_text" not in request_data:
            return jsonify({"error": "No extracted text provided. Perform OCR first."}), 400

        extracted_text = request_data["extracted_text"]
        print("Extracted Text Received:", extracted_text)

        # Perform entity recognition
        raw_entities = entity_recognition.extract_entities_from_text(extracted_text, GEMINI_API_KEY)
        print("Extracted Entities:", raw_entities)
      
        if not raw_entities:
            print("No entities were extracted.")
            return jsonify({"message": "No entities were recognized in the provided text.", "entities": []}), 200   

        entities = []
        if isinstance(raw_entities, list):  # Handle list of strings
           for entity in raw_entities:
             entities.extend([{"Entity": line.strip()} for line in entity.split("\n") if line.strip()])
        elif isinstance(raw_entities, str):  # Handle single string
          entities = [{"Entity": line.strip()} for line in raw_entities.split("\n") if line.strip()]
        else:
          entities = []
        print("Processed Entities (debug):", entities)
        
        # Store entities in session for rendering on the next page
        session['entities'] = entities
        if not entities:
            print("No entities were extracted.")
            session['entities'] = []  # Store empty list in session
            return jsonify({"message": "No entities were recognized in the provided text.", "entities": []}), 200
        
        return jsonify({"redirect_url": url_for('result_page')})
    
        # return jsonify({"extracted_entities": entities})

    except Exception as e:
        print(f"Error during entity recognition: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/display-entities')
def result_page():
    entities = session.get('entities')
    print("Formatted Entities Sent to Template:", entities)  
    return render_template("result.html", entities=entities)


if __name__ == "__main__":
    app.run(debug=True)
