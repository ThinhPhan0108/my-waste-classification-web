from tensorflow.keras.models import load_model
import tensorflow_hub as hub

try:
    # Tải mô hình với custom_objects
    model = load_model('model.h5', custom_objects={'KerasLayer': hub.KerasLayer})
    print("Model loaded successfully!")
except Exception as e:
    print(f"Error loading model: {e}")
