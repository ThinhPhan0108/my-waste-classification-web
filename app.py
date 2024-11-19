from flask import Flask, request, render_template, url_for, redirect, session, flash
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
import os
<<<<<<< HEAD
import numpy as np
from PIL import Image
from datetime import datetime
import tensorflow as tf  # Use TensorFlow directly
import tensorflow_hub as hub  # Import TensorFlow Hub
=======
import tensorflow as tf
import numpy as np
from PIL import Image
from datetime import datetime
>>>>>>> e38fbaee9cbb958e7919c4c6579f092a5bb74026

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './uploads'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///waste_classification.db'
app.secret_key = 'your_secret_key'
db = SQLAlchemy(app)

<<<<<<< HEAD
# User Model
=======
# Mô hình User
>>>>>>> e38fbaee9cbb958e7919c4c6579f092a5bb74026
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    points = db.Column(db.Integer, default=0)

<<<<<<< HEAD
# CustomerData Model
=======
# Mô hình CustomerData
>>>>>>> e38fbaee9cbb958e7919c4c6579f092a5bb74026
class CustomerData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    email = db.Column(db.String(150), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.String(255), nullable=True)
<<<<<<< HEAD
    user = db.relationship("User", backref="customer_data")  # Fixed: Removed space

# UserActivity Model
=======
    
    user = db.relationship("User", backref="customer_data")

# Mô hình UserActivity
>>>>>>> e38fbaee9cbb958e7919c4c6579f092a5bb74026
class UserActivity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    action = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
<<<<<<< HEAD
    user = db.relationship("User", backref="activities")  # Fixed: Removed space

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
    print("Model inputs:", model.input)  # Kiểm tra chi tiết đầu vào
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
        # Mở ảnh và xử lý
        image = Image.open(image_path).convert("RGB")
        image = image.resize((224, 224))  # Resize image to 224x224
        image = np.array(image) / 255.0  # Normalize image
        image = np.expand_dims(image, axis=0)  # Add batch dimension

        # Tạo đầu vào thứ hai (cùng định dạng với đầu vào thứ nhất)
        input_2 = image.copy()  # Sao chép cùng ảnh cho đầu vào thứ hai (hoặc thay bằng ảnh khác)

        if model:
            predictions = model.predict([image, input_2])  # Truyền cả 2 đầu vào
            print(f"Predictions: {predictions}")  # Print probabilities for each class
            class_idx = np.argmax(predictions)  # Index of the highest predicted class
            result = waste_types.get(class_idx, "Không xác định")  # Get class name from dictionary
            print(f"Classification result: {result}")  # Print final result
            return result
        else:
            print("Model not loaded.")  # If model is not loaded
            return "Không xác định"
=======
    
    user = db.relationship("User", backref="activities")

with app.app_context():
    db.create_all()

model = tf.keras.models.load_model('waste_classification_model.h5')
waste_types = {0: "Plastic", 1: "Glass", 2: "Metal"}

def classify_image(image_path):
    try:
        image = Image.open(image_path).convert("RGB")
        image = image.resize((224, 224))
        image = np.array(image) / 255.0
        image = np.expand_dims(image, axis=0)
        predictions = model.predict(image)
        class_idx = np.argmax(predictions)
        return waste_types.get(class_idx, "Không xác định")
>>>>>>> e38fbaee9cbb958e7919c4c6579f092a5bb74026
    except Exception as e:
        print(f"Error during classification: {e}")
        return None

<<<<<<< HEAD
# Register, Login, Logout, Home, Upload, Leaderboard, History, Admin routes...

=======
>>>>>>> e38fbaee9cbb958e7919c4c6579f092a5bb74026
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        email = request.form['email'].strip()
        phone = request.form['phone'].strip()
        address = request.form['address'].strip()

        if not username:
            flash("Tên tài khoản không được để trống!", "danger")
            return redirect('/register')

        if User.query.filter_by(username=username).first():
            flash("Tên tài khoản đã tồn tại!", "danger")
            return redirect('/register')

        new_user = User(username=username)
        db.session.add(new_user)
        db.session.commit()

        customer_data = CustomerData(user_id=new_user.id, email=email, phone=phone, address=address)
        db.session.add(customer_data)
        db.session.commit()

        flash("Đăng ký thành công! Bạn có thể đăng nhập.", "success")
        return redirect('/login')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        user = User.query.filter_by(username=username).first()

        if not user:
            flash("Tên tài khoản không tồn tại!", "danger")
            return redirect('/login')

        session['user_id'] = user.id
        flash(f"Xin chào {username}, bạn đã đăng nhập thành công!", "success")
        return redirect('/home')
    return render_template('login.html')

@app.route('/logout')
def logout():
    if 'user_id' in session:
        user_id = session.pop('user_id')
        activity = UserActivity(user_id=user_id, action="Đăng xuất")
        db.session.add(activity)
        db.session.commit()
    flash("Bạn đã đăng xuất thành công!", "info")
    return redirect('/login')

@app.route('/home')
def home():
    if 'user_id' not in session:
        return redirect('/login')

<<<<<<< HEAD
    user = db.session.get(User, session['user_id'])

=======
    user = User.query.get(session['user_id'])
>>>>>>> e38fbaee9cbb958e7919c4c6579f092a5bb74026
    is_admin = user.username == "admin"
    return render_template('home.html', is_admin=is_admin)

@app.route('/', methods=['GET', 'POST'])
def upload_image():
    if 'user_id' not in session:
        flash("Vui lòng đăng nhập để sử dụng chức năng này!", "warning")
        return redirect('/login')

<<<<<<< HEAD
    user = db.session.get(User, session['user_id'])
=======
    user = User.query.get(session['user_id'])
>>>>>>> e38fbaee9cbb958e7919c4c6579f092a5bb74026
    is_admin = user.username == "admin"

    if request.method == 'POST':
        if 'file' not in request.files:
            flash("Không có tệp được tải lên!", "danger")
            return redirect('/')

        file = request.files['file']
        if file.filename == '':
            flash("Không có tệp nào được chọn!", "danger")
            return redirect('/')

        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
<<<<<<< HEAD
            print(f"File saved at: {filepath}")  # Corrected variable reference
            
            # Di chuyển ảnh vào thư mục static/uploads
            static_path = os.path.join('static', 'uploads', filename)
            if not os.path.exists(os.path.dirname(static_path)):
                os.makedirs(os.path.dirname(static_path))  # Tạo thư mục nếu chưa có
            os.rename(filepath, static_path)  # Di chuyển tệp vào static/uploads

            result = classify_image(static_path)  # Sử dụng static_path để phân loại
=======

            result = classify_image(filepath)
>>>>>>> e38fbaee9cbb958e7919c4c6579f092a5bb74026

            if result:
                user.points += 10
                db.session.commit()

                activity = UserActivity(user_id=user.id, action=f"Phân loại: {result}")
                db.session.add(activity)
                db.session.commit()

                return render_template('result.html', result=result, image_url=url_for('static', filename=f'uploads/{filename}'), is_admin=is_admin)
            else:
                flash("Lỗi trong quá trình phân loại, vui lòng thử lại!", "danger")
    return render_template('upload.html', is_admin=is_admin)

@app.route('/leaderboard')
def leaderboard():
    users = User.query.order_by(User.points.desc()).all()
    is_admin = 'user_id' in session and User.query.get(session['user_id']).username == "admin"
    return render_template('leaderboard.html', users=users, is_admin=is_admin)

@app.route('/history')
def history():
    if 'user_id' not in session:
        flash("Vui lòng đăng nhập để xem lịch sử hoạt động!", "warning")
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
        return "Bạn không có quyền truy cập!", 403

    users = User.query.all()
    customer_data = CustomerData.query.all()
    activities = UserActivity.query.order_by(UserActivity.timestamp.desc()).all()

    return render_template('admin.html', users=users, customer_data=customer_data, activities=activities, is_admin=True)

# Ensure the app listens on the correct port for Render
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
