import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, GlobalAveragePooling2D
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.callbacks import EarlyStopping
import os

# Đường dẫn đến thư mục dữ liệu huấn luyện và kiểm tra
train_dir = 'data/train'  # Thư mục chứa các thư mục con của từng loại rác
validation_dir = 'data/validation'  # Thư mục chứa dữ liệu kiểm tra

# Tạo ImageDataGenerator để xử lý và tăng cường dữ liệu
train_datagen = ImageDataGenerator(
    rescale=1.0/255.0,
    rotation_range=30,
    width_shift_range=0.2,
    height_shift_range=0.2,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True,
    fill_mode='nearest'
)

validation_datagen = ImageDataGenerator(rescale=1.0/255.0)

# Đặt kích thước batch và kích thước ảnh
batch_size = 32
img_height = 224
img_width = 224

# Chuẩn bị dữ liệu huấn luyện và kiểm tra
train_generator = train_datagen.flow_from_directory(
    train_dir,
    target_size=(img_height, img_width),
    batch_size=batch_size,
    class_mode='categorical'
)

validation_generator = validation_datagen.flow_from_directory(
    validation_dir,
    target_size=(img_height, img_width),
    batch_size=batch_size,
    class_mode='categorical'
)

# Sử dụng MobileNetV2 với trọng số được huấn luyện sẵn trên ImageNet
base_model = MobileNetV2(weights='imagenet', include_top=False, input_shape=(img_height, img_width, 3))
base_model.trainable = False  # Đóng băng các lớp của MobileNetV2

# Xây dựng model
model = Sequential([
    base_model,
    GlobalAveragePooling2D(),
    Dense(128, activation='relu'),
    Dropout(0.5),
    Dense(train_generator.num_classes, activation='softmax')
])

# Biên dịch model
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

# Sử dụng Early Stopping để tránh overfitting
early_stopping = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)

# Huấn luyện model
epochs = 30
history = model.fit(
    train_generator,
    steps_per_epoch=train_generator.samples // batch_size,
    epochs=epochs,
    validation_data=validation_generator,
    validation_steps=validation_generator.samples // batch_size,
    callbacks=[early_stopping]
)

# Lưu model
model.save('waste_classification_model_transfer_learning.h5')
print("Model đã được lưu thành công.")
