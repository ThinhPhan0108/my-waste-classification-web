from flask import Flask, request, render_template, url_for, redirect, session, flash
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
import os
import numpy as np
from PIL import Image
from datetime import datetime
import tensorflow as tf
import tensorflow_hub as hub
import json
import logging
import base64
from datetime import datetime
import os
import requests
import gdown
import platform

def get_temp_folder():
    """
    Trả về đường dẫn thư mục tạm tùy thuộc vào hệ điều hành.
    """
    if platform.system() == "Windows":
        temp_folder = os.path.join(os.getcwd(), ".tmp")  # Local Windows sử dụng .tmp
    else:
        temp_folder = "/tmp"  # Render sử dụng /tmp
    os.makedirs(temp_folder, exist_ok=True)  # Tạo thư mục nếu chưa tồn tại
    return temp_folder

def download_model():
    """
    Tải xuống mô hình từ Google Drive nếu nó chưa tồn tại trong thư mục tạm.
    """
    url = "https://drive.google.com/uc?id=1rtxHkF5zr6nuqOwVGkcZwDowgArZnhLH"
    temp_folder = get_temp_folder()
    output = os.path.join(temp_folder, "model.h5")

    if not os.path.exists(output):  # Kiểm tra nếu tệp chưa tồn tại
        print("Downloading model...")
        gdown.download(url, output, quiet=False)
        print("Model downloaded successfully!")
    else:
        print("Model already exists.")

    # Kiểm tra kích thước tệp
    if os.path.exists(output):
        print(f"Downloaded file size: {os.path.getsize(output)} bytes")
    return output


# Setup logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './uploads'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///waste_classification.db'
app.secret_key = 'your_secret_key'
db = SQLAlchemy(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    points = db.Column(db.Integer, default=0)

class CustomerData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    email = db.Column(db.String(150), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.String(255), nullable=True)
    user = db.relationship("User", backref="customer_data")

class UserActivity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    action = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship("User", backref="activities")

# Ensure the database is created
with app.app_context():
    db.create_all()

# Load Model
def load_model(model_path, custom_objects=None):
    try:
        model = tf.keras.models.load_model(model_path, custom_objects=custom_objects)
        logging.info("Model loaded successfully!")
        return model
    except Exception as e:
        logging.error(f"Error loading model: {e}")
        return None

model = load_model("model.h5", custom_objects={"KerasLayer": hub.KerasLayer})

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

# Load thông tin từ file JSON
def get_waste_info():
    try:
        with open('waste_info.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Error loading JSON: {e}")
        return {}

waste_info = get_waste_info()

def classify_image(image_path):
    try:
        # Load and preprocess the image
        image = Image.open(image_path).convert("RGB")
        image = image.resize((224, 224))  # Resize image to the required size
        image = np.array(image) / 255.0  # Normalize pixel values
        image = np.expand_dims(image, axis=0)  # Add batch dimension

        # Prepare a second identical input tensor (if required by the model)
        input_2 = image.copy()  # Use the same image as the second input

        # Pass both inputs to the model
        if model:
            predictions = model.predict([image, input_2])  # Model expects two inputs
            class_idx = np.argmax(predictions)  # Get the index of the highest probability
            return waste_types.get(class_idx, "Unknown")
        else:
            logging.error("Model not loaded.")
            return "Unknown"
    except Exception as e:
        logging.error(f"Error during classification: {e}")
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
        flash("Vui lòng đăng nhập để sử dụng tính năng này!", "warning")
        return redirect('/login')

    user = db.session.get(User, session['user_id'])
    is_admin = user.username == "admin"

    if request.method == 'POST':
        # Xử lý ảnh chụp từ camera (Base64)
        captured_image = request.form.get('captured_image')
        if captured_image:
            try:
                # Decode Base64 và lưu file
                image_data = base64.b64decode(captured_image.split(',')[1])
                filename = f"captured_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                with open(filepath, "wb") as f:
                    f.write(image_data)

                # Chuyển file sang static/uploads để sử dụng trên giao diện web
                static_path = os.path.join('static', 'uploads', filename)
                os.makedirs(os.path.dirname(static_path), exist_ok=True)
                if not os.path.exists(static_path):
                    os.rename(filepath, static_path)

                # Phân loại ảnh
                result = classify_image(static_path)

                if result:
                    # Cộng điểm cho người dùng
                    user.points += 10
                    db.session.commit()

                    # Lưu hoạt động người dùng
                    activity = UserActivity(user_id=user.id, action=f"Phân loại: {result}")
                    db.session.add(activity)
                    db.session.commit()

                    # Lấy thông tin chi tiết từ JSON
                    waste_details = waste_info.get(result, {})
                    description = waste_details.get("description", "Thông tin không khả dụng.")
                    environmental_impact = waste_details.get("environmental_impact", "Không có thông tin về tác động môi trường.")
                    tips = waste_details.get("tips", "Không có mẹo xử lý.")
                    recycle_centers = waste_details.get("recycle_centers", [])

                    # Trả về kết quả
                    return render_template(
                        'result.html',
                        result=result,
                        description=description,
                        environmental_impact=environmental_impact,
                        tips=tips,
                        recycle_centers=recycle_centers,
                        image_url=url_for('static', filename=f'uploads/{filename}'),
                        is_admin=is_admin
                    )
                else:
                    flash("Xảy ra lỗi trong quá trình phân loại. Vui lòng thử lại!", "danger")
            except Exception as e:
                flash(f"Lỗi xử lý ảnh từ camera: {e}", "danger")
                return redirect('/')

        # Xử lý ảnh tải lên từ file
        file = request.files.get('file')
        if file and file.filename != '':
            # Lưu file vào thư mục uploads
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Chuyển file sang static/uploads để sử dụng trên giao diện web
            static_path = os.path.join('static', 'uploads', filename)
            os.makedirs(os.path.dirname(static_path), exist_ok=True)
            if not os.path.exists(static_path):
                os.rename(filepath, static_path)

            # Phân loại ảnh
            result = classify_image(static_path)

            if result:
                # Cộng điểm cho người dùng
                user.points += 10
                db.session.commit()

                # Lưu hoạt động người dùng
                activity = UserActivity(user_id=user.id, action=f"Phân loại: {result}")
                db.session.add(activity)
                db.session.commit()

                # Lấy thông tin chi tiết từ JSON
                waste_details = waste_info.get(result, {})
                description = waste_details.get("description", "Thông tin không khả dụng.")
                environmental_impact = waste_details.get("environmental_impact", "Không có thông tin về tác động môi trường.")
                tips = waste_details.get("tips", "Không có mẹo xử lý.")
                recycle_centers = waste_details.get("recycle_centers", [])

                # Trả về kết quả
                return render_template(
                    'result.html',
                    result=result,
                    description=description,
                    environmental_impact=environmental_impact,
                    tips=tips,
                    recycle_centers=recycle_centers,
                    image_url=url_for('static', filename=f'uploads/{filename}'),
                    is_admin=is_admin
                )
            else:
                flash("Xảy ra lỗi trong quá trình phân loại. Vui lòng thử lại!", "danger")
        else:
            flash("Chưa chọn tệp hoặc chụp ảnh!", "danger")
    # Hiển thị giao diện upload
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

# Thay đổi trong phần khởi động ứng dụng
if __name__ == "__main__":
    try:
        model_path = download_model()  # Nhận đường dẫn model
        model = load_model(model_path, custom_objects={"KerasLayer": hub.KerasLayer})  # Load model từ đường dẫn
        print("Model loaded successfully!")
    except Exception as e:
        print(f"Error initializing the application: {e}")
        exit(1)

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)






