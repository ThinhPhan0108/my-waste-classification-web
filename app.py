from flask import Flask, request, render_template, url_for, redirect, session, flash
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
import os
import numpy as np
from PIL import Image
from datetime import datetime
import tensorflow as tf  # Use TensorFlow directly
import tensorflow_hub as hub  # Import TensorFlow Hub

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './uploads'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///waste_classification.db'
app.secret_key = 'your_secret_key'
db = SQLAlchemy(app)

# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    points = db.Column(db.Integer, default=0)

# CustomerData Model
class CustomerData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    email = db.Column(db.String(150), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.String(255), nullable=True)
    user = db.relationship("User", backref="customer_data")

# UserActivity Model
class UserActivity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    action = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship("User", backref="activities")

# Ensure the database is created
with app.app_context():
    db.create_all()

# Function to load the model
def load_model(model_path, custom_objects=None):
    try:
        model = tf.keras.models.load_model(model_path, custom_objects=custom_objects)
        return model
    except Exception as e:
        print(f"Error loading model: {e}")
        return None

# Load the model using TensorFlow
model = load_model("model.h5", custom_objects={"KerasLayer": hub.KerasLayer})
if model:
    print("Model loaded successfully!")
    print("Model inputs:", model.input)  # Check input details
else:
    print("Model not loaded.")

waste_types = {
    0: 'battery',
    1: 'biological',
    2: 'brown-glass',
    3: 'cardboard',
    4: 'clothes',
    5: 'green-glass',
    6: 'metal',
    7: 'paper',
    8: 'plastic',
    9: 'shoes',
    10: 'trash',
    11: 'white-glass'
}

def classify_image(image_path):
    try:
        # Process image
        image = Image.open(image_path).convert("RGB")
        image = image.resize((224, 224))
        image = np.array(image) / 255.0
        image = np.expand_dims(image, axis=0)

        # Duplicate the image for the second input
        input_2 = image.copy()

        if model:
            predictions = model.predict([image, input_2])
            print(f"Predictions: {predictions}")
            class_idx = np.argmax(predictions)
            result = waste_types.get(class_idx, "Unknown")
            print(f"Classification result: {result}")
            return result
        else:
            print("Model not loaded.")
            return "Unknown"
    except Exception as e:
        print(f"Error during classification: {e}")
        return None

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        email = request.form['email'].strip()
        phone = request.form['phone'].strip()
        address = request.form['address'].strip()

        if not username:
            flash("Username cannot be empty!", "danger")
            return redirect('/register')

        if User.query.filter_by(username=username).first():
            flash("Username already exists!", "danger")
            return redirect('/register')

        new_user = User(username=username)
        db.session.add(new_user)
        db.session.commit()

        customer_data = CustomerData(user_id=new_user.id, email=email, phone=phone, address=address)
        db.session.add(customer_data)
        db.session.commit()

        flash("Registration successful! You can now log in.", "success")
        return redirect('/login')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        user = User.query.filter_by(username=username).first()

        if not user:
            flash("Username does not exist!", "danger")
            return redirect('/login')

        session['user_id'] = user.id
        flash(f"Welcome {username}, you have successfully logged in!", "success")
        return redirect('/home')
    return render_template('login.html')

@app.route('/logout')
def logout():
    if 'user_id' in session:
        user_id = session.pop('user_id')
        activity = UserActivity(user_id=user_id, action="Logged out")
        db.session.add(activity)
        db.session.commit()
    flash("Successfully logged out!", "info")
    return redirect('/login')

@app.route('/home')
def home():
    if 'user_id' not in session:
        return redirect('/login')

    user = db.session.get(User, session['user_id'])
    is_admin = user.username == "admin"
    return render_template('home.html', is_admin=is_admin)

@app.route('/', methods=['GET', 'POST'])
def upload_image():
    if 'user_id' not in session:
        flash("Please log in to use this feature!", "warning")
        return redirect('/login')

    user = db.session.get(User, session['user_id'])
    is_admin = user.username == "admin"

    if request.method == 'POST':
        if 'file' not in request.files:
            flash("No file uploaded!", "danger")
            return redirect('/')

        file = request.files['file']
        if file.filename == '':
            flash("No file selected!", "danger")
            return redirect('/')

        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            print(f"File saved at: {filepath}")

            # Move file to static/uploads for serving
            static_path = os.path.join('static', 'uploads', filename)
            if not os.path.exists(os.path.dirname(static_path)):
                os.makedirs(os.path.dirname(static_path))
            os.rename(filepath, static_path)

            result = classify_image(static_path)

            if result:
                user.points += 10
                db.session.commit()

                activity = UserActivity(user_id=user.id, action=f"Classified: {result}")
                db.session.add(activity)
                db.session.commit()

                return render_template('result.html', result=result, image_url=url_for('static', filename=f'uploads/{filename}'), is_admin=is_admin)
            else:
                flash("Error during classification. Please try again!", "danger")
    return render_template('upload.html', is_admin=is_admin)

@app.route('/leaderboard')
def leaderboard():
    users = User.query.order_by(User.points.desc()).all()
    is_admin = 'user_id' in session and User.query.get(session['user_id']).username == "admin"
    return render_template('leaderboard.html', users=users, is_admin=is_admin)

@app.route('/history')
def history():
    if 'user_id' not in session:
        flash("Please log in to view activity history!", "warning")
        return redirect('/login')

    user_id = session['user_id']
    activities = UserActivity.query.filter_by(user_id=user_id).order_by(UserActivity.timestamp.desc()).all()
    is_admin = User.query.get(user_id).username == "admin"
    return render_template('history.html', activities=activities, is_admin=is_admin)

@app.route('/admin')
def admin_dashboard():
    if 'user_id' not in session:
        return redirect('/login')

    admin_user = User.query.get(session['user_id'])
    if admin_user.username != "admin":
        return "You do not have access!", 403

    users = User.query.all()
    customer_data = CustomerData.query.all()
    activities = UserActivity.query.order_by(UserActivity.timestamp.desc()).all()

    return render_template('admin.html', users=users, customer_data=customer_data, activities=activities, is_admin=True)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
