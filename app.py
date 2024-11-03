from flask import Flask, render_template
from flask import Flask, request, render_template, jsonify
import requests
from flask_sqlalchemy import SQLAlchemy

from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mail import Mail, Message # type: ignore
import random
import string

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a secure key
# Configure the database URI
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define the User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)  

# Create the database and tables
with app.app_context():
    db.create_all()

# Simulated user storage
users_db = {}

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        # Authenticate user
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:  # Replace with hashed password check in production
            session['user'] = email
            flash('Logged in successfully!')
            return redirect(url_for('home'))
        
        flash('Invalid email or password.')
        return redirect(url_for('login'))
    
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')  # Use .get() to avoid KeyError
        password = request.form.get('password')  # Use .get() to avoid KeyError

        if not email or not password:
            flash('Email is required.', 'error')
            return redirect(url_for('login'))

        # Check if email already exists
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'error')
            return redirect(url_for('signup'))

        # Create and store new user
        new_user = User(email, password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful!', 'success')
        return redirect(url_for('login'))

    return render_template('signup.html')


@app.route('/')
def home():
    return  render_template('index.html')

@app.route('/upload')
def upload():
   return render_template('upload.html')

# app = Flask(__name__)
# app.secret_key = 'your_secret_key'  

# Configure Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False  # Ensure this is False, as only TLS is used
app.config['MAIL_USERNAME'] = 'your_email@gmail.com'
app.config['MAIL_PASSWORD'] = 'your_email_password_or_app_password'
mail = Mail(app)

# Dummy database (for demonstration)
users_db = {
    'user@example.com': 'old_password'  # Replace with your user data source
}

def generate_random_password(length=8):
    """Generate a random password."""
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for _ in range(length))

def find_user_by_email(email):
    """Return the exact key in users_db if a case-insensitive match is found."""
    for stored_email in users_db.keys():
        if stored_email.lower() == email.lower():
            return stored_email
    return None

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        print("Email received:", email)  # Debugging

        # Find user by email in a case-insensitive manner
        stored_email = find_user_by_email(email)

        if stored_email:
            new_password = generate_random_password()
            users_db[stored_email] = new_password  # Update the password in your user database
            
            # Send the new password via email
            try:
                msg = Message('Your New Password', sender=app.config['MAIL_USERNAME'], recipients=[email])
                msg.body = f'Your new password is: {new_password}'
                mail.send(msg)
                flash('A new password has been sent to your email.', 'success')
            except Exception as e:
                print("Error sending email:", e)
                flash('There was an error sending the email. Please try again.', 'error')

            return redirect(url_for('forgot-password'))
        else:
            flash('Email not found.', 'error')

    return render_template('forget.html')


if __name__ == '__main__':
    app.run(debug=True)


# @app.route('/')
# def hello():
#     return render_template('index.html')
# @app.route('/signup')  
# def signup():
#     return render_template('signup.html')

# @app.route('/upload')
# def upload():
#    return render_template('upload.html')

# Replace with your actual OCR API URL
# OCR_API_URL = "http://127.0.0.1:8000/ocr"



# @app.route('/apply-ocr', methods=['POST'])
# def apply_ocr():
#     # Get the image file from the form data
#     image_file = request.files.get('image')
#     if not image_file:
#         return jsonify({"error": "No image file uploaded"}), 400
    
#     # Send the image file to the OCR API
#     response = requests.post(OCR_API_URL, files={'file': image_file})
    
#     if response.status_code == 200:
#         # Assuming the OCR API returns JSON with the OCR result
#         ocr_result = response.json().get('text', 'No text found')
#         return jsonify({"result": ocr_result})
#     else:
#         return jsonify({"error": "OCR failed"}), response.status_code

# if __name__ == '__main__':
#     app.run(debug=True)


