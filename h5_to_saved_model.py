import tensorflow as tf
import tensorflow_hub as hub  # Để hỗ trợ KerasLayer

# Load model từ file model.h5 với custom_objects
model = tf.keras.models.load_model(
    "model.h5", custom_objects={"KerasLayer": hub.KerasLayer}
)

# Chuyển đổi và lưu dưới định dạng SavedModel
saved_model_path = "saved_model"
model.save(saved_model_path, save_format="tf")

print(f"Model đã được lưu dưới dạng SavedModel tại: {saved_model_path}")
