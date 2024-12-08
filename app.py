from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename
from steg_utils import encode_message_in_image, decode_message_from_image, encrypt_message, decrypt_message, generate_key
from models import db, User, Image
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key'
app.config['UPLOAD_FOLDER'] = 'static/uploads/'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/encode', methods=['GET', 'POST'])
def encode():
    if request.method == 'POST':
        image = request.files['image']
        message = request.form['message']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            return "Passwords do not match!"

        # Generate key and encrypt the message
        key, salt = generate_key(password)
        encrypted_message = encrypt_message(message, key)

        # Save uploaded image
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(image.filename))
        image.save(image_path)

        # Encode the message in the image
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], 'encoded_' + secure_filename(image.filename))
        encode_message_in_image(image_path, encrypted_message, output_path)
        return "Message successfully encoded!"

    return render_template('encode.html')

@app.route('/decode', methods=['GET', 'POST'])
def decode():
    if request.method == 'POST':
        image = request.files['image']
        password = request.form['password']

        # Save uploaded image
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(image.filename))
        image.save(image_path)

        # Decode the message from the image
        encrypted_message = decode_message_from_image(image_path)

        # Generate key and decrypt the message
        key, _ = generate_key(password)
        try:
            message = decrypt_message(encrypted_message, key)
            return f"Decoded Message: {message.decode()}"
        except Exception as e:
            return "Failed to decode the message. Invalid password or corrupted image."

    return render_template('decode.html')

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        # Placeholder for image search implementation
        return "Search functionality to be implemented!"
    return render_template('search.html')

if __name__ == '__main__':
    app.run(debug=True)
